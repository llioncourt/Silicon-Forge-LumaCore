#!/usr/bin/env python3
"""Silicon Forge | Photon Mono M7 Pro .pwsz PW0 calibration-coupon patcher.
Stdlib-only. EXPERIMENTAL. No slicing, no STL-to-PWSZ fabrication.
Designed to preserve the original job/profile while editing the pixel gray
levels of a 90x24x4 mm CONTROL coupon, not a complete sculpture.
"""
from __future__ import annotations
import copy
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import zipfile

W, H = 13312, 5120
PIXELS = W * H
TARGET_THICKNESS_MM = .05
TARGET_EXPOSURE_S = 1.8
LAYER_RE = re.compile(r'^layer_images/layer_(\d+)\.(pw0Img|pwszImg)$', re.I)

def fail(message):
    raise ValueError(message)

def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()

def iter_rle(data):
    pos = 0
    cursor = 0
    while pos < len(data):
        code = data[pos]; pos += 1
        shade = code >> 4
        n = code & 15
        if shade in (0, 15):
            if pos >= len(data):
                fail('RLE PW0 truncado')
            n = n * 256 + data[pos]
            pos += 1
        if not n:
            fail('RLE PW0 com repeticao zero')
        end = cursor + n
        if end > PIXELS:
            fail('Camada PW0 ultrapassa o LCD')
        yield cursor, end, shade
        cursor = end
    if cursor != PIXELS:
        fail(f'Camada PW0 incompleta: {cursor} de {PIXELS} pixels')

def encode_runs(segments):
    out = bytearray()
    prev_shade = None
    prev_n = 0
    def emit(shade, n):
        if n <= 0:
            return
        cap = 4095 if shade in (0, 15) else 15
        while n:
            take = min(n, cap)
            if shade in (0, 15):
                out.extend((shade * 16 + (take >> 8), take & 255))
            else:
                out.append(shade * 16 + take)
            n -= take
    for n, shade in segments:
        if n <= 0: continue
        if shade < 0 or shade > 15: fail('Tom fora de 4 bits')
        if shade == prev_shade:
            prev_n += n
        else:
            if prev_shade is not None: emit(prev_shade, prev_n)
            prev_shade, prev_n = shade, n
    if prev_shade is not None: emit(prev_shade, prev_n)
    return bytes(out)

def inspect_rle(data):
    xmin, xmax = W, 0
    ymin, ymax = H, 0
    count_on = 0
    for start, end, shade in iter_rle(data):
        if shade == 0: continue
        count_on += end - start
        firstrow, lastrow = divmod(start, W)[0], (end - 1) // W
        firstcol, lastcol = start % W, (end - 1) % W
        if firstrow == lastrow:
            xmin = min(xmin, firstcol)
            xmax = max(xmax, lastcol + 1)
        else:
            xmin = 0
            xmax = W
        ymin = min(ymin, firstrow)
        ymax = max(ymax, lastrow + 1)
    if count_on == 0: return None
    return (xmin, ymin, xmax, ymax, count_on)

def write_partition(out, start, end, shade, changes, tally):
    cursor = start
    for lo, hi, replacement in changes:
        if lo >= end or hi <= cursor: continue
        lo = max(lo, cursor)
        hi = min(hi, end)
        if hi <= lo: continue
        if cursor < lo:
            out.append((lo - cursor, shade))
        if shade == 15:
            out.append((hi - lo, replacement))
            tally[replacement] = tally.get(replacement, 0) + hi - lo
        else:
            out.append((hi - lo, shade))
        cursor = hi
    if cursor < end:
        out.append((end - cursor, shade))

def patch_coupon_layer(raw, layer_index, total_layers, bottom_layers, transition_layers, pixx_mm, pixy_mm):
    first_mod = max(bottom_layers + transition_layers, math.ceil(1.0 / TARGET_THICKNESS_MM))
    last_mod = total_layers - math.ceil(.6 / TARGET_THICKNESS_MM)
    if not first_mod <= layer_index < last_mod:
        return raw, {'pixels_changed': 0, 'reason': 'zona de seguranca (base/topo/transicao)'}
    bbox = inspect_rle(raw)
    if bbox is None:
        fail(f'Camada {layer_index}: vazia; cupom mal fatiado')
    x0, y0, x1, y1, oncount = bbox
    dx = (x1 - x0) * pixx_mm
    dy = (y1 - y0) * pixy_mm
    density = oncount / ((x1 - x0) * (y1 - y0))
    if not (86 <= dx <= 94 and 21 <= dy <= 27 and density >= .98):
        fail(f'Camada {layer_index}: {dx:.1f} x {dy:.1f} mm, preenchimento={density:.3f}. Nao parece o cupom unico 90x24mm')
    guard_x = math.ceil(1.5 / pixx_mm)
    guard_y = math.ceil(1.5 / pixy_mm)
    third1 = x0 + (x1-x0)//3
    third2 = x0 + 2*(x1-x0)//3
    bands = ((third1 + guard_x, third2 - guard_x, 14),
             (third2 + guard_x, x1 - guard_x, 13))
    if any(lo >= hi for lo,hi,_ in bands): fail('Cupom pequeno demais para margens')
    ylo, yhi = y0 + guard_y, y1 - guard_y
    if ylo >= yhi: fail('Cupom estreito demais na direcao Y')
    out_segments = []
    tally = {}
    for start, end, shade in iter_rle(raw):
        if shade != 15 or end <= ylo*W or start >= yhi*W:
            out_segments.append((end-start, shade))
            continue
        cursor = start
        while cursor < end:
            row = cursor // W
            row_end = min(end, (row+1)*W)
            if row < ylo or row >= yhi:
                out_segments.append((row_end-cursor, shade))
            else:
                changes = [(row*W+left,row*W+right,tone) for left,right,tone in bands]
                write_partition(out_segments, cursor, row_end, shade, changes, tally)
            cursor=row_end
    patched = encode_runs(out_segments)
    if sum(end-start for start,end,shade in iter_rle(patched)) != PIXELS: fail('Perda de pixels')
    if not tally:
        fail(f'Camada {layer_index}: nenhuma microdosagem aplicada')
    before, after = inspect_rle(raw), inspect_rle(patched)
    if before != after: fail('Contorno ou area de suporte sofreu alteracao')
    if not set(tally).issubset({13,14}): fail('Nivel de cinza inesperado')
    return patched, {'pixels_changed': sum(tally.values()), 'levels_nibble': dict(sorted(tally.items())),
                     'bbox_mm': [round(dx,3),round(dy,3)],'preserved_mask':True}

def validate_archive(source):
    source = Path(source)
    if source.suffix.lower() != '.pwsz': fail('Arquivo deve ser .pwsz')
    if not zipfile.is_zipfile(source): fail('Arquivo .pwsz nao eh ZIP valido')
    z = zipfile.ZipFile(source)
    names = z.namelist()
    if len(set(names)) != len(names): fail('Entradas ZIP repetidas')
    for required in ('anycubic_photon_resins.pwsp','layers_controller.conf','scene.slice','print_info.json'):
        if required not in names: fail(f'Metadados nativos ausentes: {required}')
    cfg = json.loads(z.read('anycubic_photon_resins.pwsp'))
    ctl = json.loads(z.read('layers_controller.conf'))
    machine = cfg.get('machine_type',{})
    if (machine.get('res_x'),machine.get('res_y')) != (W,H): fail('Resolucao nao corresponde a M7 Pro')
    if 'M7' not in machine.get('name','').upper() or 'PRO' not in machine.get('name','').upper():
        fail('Impressora nao identificada como Photon Mono M7 Pro')
    layers={}
    for name in names:
        m=LAYER_RE.fullmatch(name)
        if m:
            i=int(m.group(1))
            if i in layers: fail(f'Indice duplicado de camada: {i}')
            layers[i]=(name,m.group(2).lower())
    if not layers: fail('Nenhuma camada encontrada')
    if set(layers)!=set(range(len(layers))): fail('Camadas nao sequenciais')
    if ctl.get('count') != len(layers): fail('Quantidade de camadas no controller diverge das imagens')
    paras=ctl.get('paras',[])
    if len(paras) != len(layers) or any(int(r.get('layer_index',-1))!=i for i,r in enumerate(paras)):
        fail('Controller possui indices ou numero de camadas inconsistentes')
    extern=cfg.get('machine_extern',{})
    active=extern.get('active_resins',[])
    found=[]
    for group in (extern.get('user_resins',[]),extern.get('factory_resins',[])):
        matches=[]
        for r in group:
            prop=r.get('property',{})
            if prop.get('name') in active or prop.get('code') in active:
                matches.append(r)
        if matches:
            found=matches
            break
    if len(found)!=1:
        fail('Nao foi possivel identificar exatamente um perfil de resina ativo')
    prop=found[0].get('property',{})
    settings=found[0].get('slicepara',{})
    if 'standard' not in (str(prop.get('name',''))+' '+str(prop.get('type',''))).lower():
        fail(f'Resina nao identificada como Standard: {prop.get("name")}')
    if abs(float(settings.get('zthick',-1))-.05)>0.0001: fail('O perfil nao esta em 0.050 mm')
    if abs(float(settings.get('exposure_time',-1))-1.8)>0.025: fail('O perfil nao esta em 1.800 s')
    if len(layers) < 70 or len(layers) > 95:
        fail('Este projeto processa apenas o cupom 4mm (~80 camadas), nao uma estatua')
    for i,r in enumerate(paras):
        if abs(float(r.get('layer_thickness',0))-.05)>.0001:
            fail(f'Camada {i}: espessura inesperada no controller')
    b=int(settings.get('bott_layers',-1))
    if not 0 <= b < 30: fail('Numero de camadas de base invalido')
    ext=found[0].get('slice_extpara',{})
    transition=int(ext.get('transition_layercount',0))
    if not 0 <= transition < 25: fail('Numero de camadas de transicao invalido')
    pixx = float(machine.get('print_xsize',223.64)) / W
    pixy = float(machine.get('print_ysize',126.48)) / H
    if not (.016 <= pixx <= .018 and .023 <= pixy <= .026): fail('Dimensoes de pixel inesperadas')
    profile={'printer':machine['name'], 'resin_profile':prop.get('name'),
        'resin_code':prop.get('code'),'film':prop.get('film_name','NAO DECLARADO NO ARQUIVO'),
        'layer_mm':float(settings['zthick']), 'normal_exposure_s':float(settings['exposure_time']),
        'bottom_layers':b,'bottom_exposure_s':settings.get('bott_time'),
        'transition_layers':transition,'resolution':[W,H],
        'pixel_pitch_mm':[pixx,pixy], 'image_codecs':sorted(set(f for _,f in layers.values())),
        'layer_count':len(layers)}
    return z, layers, profile

def inspect(source):
    z, layers, profile=validate_archive(source)
    try:
        print(json.dumps(profile,ensure_ascii=False,indent=2))
        print('Status: verificacao de metadados concluida; NAO valida gravacao na impressora')
    finally: z.close()

def patch(source,target):
    source,target=Path(source),Path(target)
    if source.resolve()==target.resolve(): fail('Arquivo original nunca pode ser sobrescrito')
    z,layers,profile=validate_archive(source)
    try:
        if profile['image_codecs'] != ['pw0img']:
            fail('Codec PWSZImg sem suporte. Fatie o cupom com AA=8/16 e confirme pw0Img.')
        target.parent.mkdir(parents=True,exist_ok=True)
        temp = target.with_name(target.name+'.part')
        audit = {'source':str(source),'source_sha256':sha256_file(source),
                 'profile':profile,'changed_layers':0,'changed_pixels':0,
                 'layers':[], 'technical_status':'APENAS TESTE SOFTWARE: impressora real nao validada'}
        try:
            with zipfile.ZipFile(temp,'w') as dest:
                for info in z.infolist():
                    raw=z.read(info.filename)
                    match=LAYER_RE.fullmatch(info.filename)
                    if match:
                        i=int(match.group(1))
                        updated, stats=patch_coupon_layer(raw,i,len(layers),profile['bottom_layers'],
                                                          profile['transition_layers'],*profile['pixel_pitch_mm'])
                        raw=updated
                        if stats['pixels_changed']:
                            audit['changed_layers']+=1
                            audit['changed_pixels']+=stats['pixels_changed']
                        audit['layers'].append({'index':i,**stats})
                    dest.writestr(copy.copy(info),raw)
            if audit['changed_layers'] < 15: fail('Poucas camadas modificadas: exame de cupom invalido')
            with zipfile.ZipFile(temp) as check:
                if check.testzip() is not None: fail('Falhou teste CRC do ZIP')
                original_names=z.namelist()
                if check.namelist()!=original_names: fail('Mudanca inesperada na estrutura de arquivos')
                for name in original_names:
                    if LAYER_RE.fullmatch(name): continue
                    if z.read(name)!=check.read(name): fail('Metadados nao deveriam ter mudado: '+name)
            os.replace(temp,target)
            audit['output_sha256']=sha256_file(target)
            audit['output_file']=str(target)
            report=target.with_name(target.stem+'_auditoria.json')
            report.write_text(json.dumps(audit,indent=2,ensure_ascii=False),encoding='utf-8')
            print('Resultado:',target)
            print('Auditoria:',report)
        finally:
            if temp.exists(): temp.unlink()
    finally: z.close()

def selftest():
    a=encode_runs(((W*H,0),))
    assert inspect_rle(a) is None
    b=encode_runs(((300,15),(100,14),(W*H-400,0)))
    assert sum(end-start for start,end,shade in iter_rle(b) if shade==15)==300
    assert sum(end-start for start,end,shade in iter_rle(b) if shade==14)==100
    assert sum(end-start for start,end,shade in iter_rle(a))==PIXELS
    pwx=223.64/W; pwy=126.48/H
    sx=int(round(90/pwx)); sy=int(round(24/pwy))
    x0=(W-sx)//2; y0=(H-sy)//2
    segs=[]
    for y in range(H):
        if y0<=y<y0+sy:
            segs.extend(((x0,0),(sx,15),(W-x0-sx,0)))
        else: segs.append((W,0))
    layer=encode_runs(segs)
    patched,detail=patch_coupon_layer(layer,21,80,5,0,pwx,pwy)
    assert detail['pixels_changed']>0
    assert inspect_rle(layer)==inspect_rle(patched)
    tones={shade for _,_,shade in iter_rle(patched)}
    assert tones=={0,13,14,15},tones
    print('AUTOTESTE APROVADO: RLE 4-bit, 68MP sem matriz em memoria, regioes internas e silhueta conservada')
    return layer,patched

def main():
    p=argparse.ArgumentParser(description='SF M7 Pro: PWSZ calibracao optica (EXPERIMENTAL). Biblioteca padrao.')
    p.add_argument('command',choices=['inspect','patch','selftest'])
    p.add_argument('source',nargs='?')
    p.add_argument('target',nargs='?')
    a=p.parse_args()
    try:
        if a.command=='selftest': selftest()
        elif a.command=='inspect':
            if not a.source: fail('Informe o .pwsz')
            inspect(a.source)
        elif a.command=='patch':
            if not a.source: fail('Informe o .pwsz original fatiado')
            target=a.target or str(Path(a.source).with_name(Path(a.source).stem+'_SF_MICRODOSE_TESTE.pwsz'))
            patch(a.source,target)
    except (ValueError,KeyError,zipfile.BadZipFile,FileNotFoundError) as e:
        print('BLOQUEADO:',e,file=sys.stderr)
        sys.exit(2)

if __name__=='__main__': main()
