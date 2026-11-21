#!/usr/bin/env python3
"""Convert an observed M7 Pro Photon Workshop 4.2 native rectangular coupon
from PWSZImg vector contours into PW0 4-bit RLE, without changing print profile.

EXPERIMENTAL. Only accepts 80 identical 4-segment rectangular contours and
rejects everything else. Output is for software validation, NOT proof of a
working printable job or of optical microdose effectiveness.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import struct
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sf_pwsz import validate_archive, encode_runs, inspect_rle, sha256_file, W, H

BASE=Path(__file__).resolve().parent
SRC=BASE/'01_CUPOM_CALIBRACAO_DOSE_UMA_PECA_ORIGINAL.pwsz'
OUT=BASE/'SF_CONTROLE_RASTER_PW0_NAO_IMPRIMIR.pwsz'
REPORT=BASE/'conversao_auditoria.json'

def parse_rectangle_vector(raw):
    if len(raw)!=124 or raw[:3]!=b'{==' or raw[32:35]!=b'[--' or raw[116:119]!=b'--]' or raw[120:123]!=b'==}':
        raise ValueError('PWSZImg fora do padrao retangular do cupom; recusado')
    if struct.unpack_from('<I',raw,40)[0]!=4:
        raise ValueError('Quantidade de segmentos divergente')
    segments=[]
    for i in range(4):
        k=48+17*i
        segments.append((struct.unpack_from('<ffff',raw,k),raw[k+16]))
    ends=[]
    for ((x0,y0,x1,y1),flag) in segments:
        if not (math.isclose(x0,x1,abs_tol=0.0001) or math.isclose(y0,y1,abs_tol=0.0001)):
            raise ValueError('Encontrada aresta nao ortogonal')
        ends.extend(((x0,y0),(x1,y1)))
    xs=sorted(set(x for x,y in ends)); ys=sorted(set(y for x,y in ends))
    if len(xs)!=2 or len(ys)!=2:
        raise ValueError('Geometria nao retangular')
    edges={tuple(sorted(((x0,y0),(x1,y1)))) for (x0,y0,x1,y1),flag in segments}
    expected={tuple(sorted((a,b))) for a,b in [((xs[0],ys[0]),(xs[1],ys[0])),((xs[1],ys[0]),(xs[1],ys[1])),((xs[1],ys[1]),(xs[0],ys[1])),((xs[0],ys[1]),(xs[0],ys[0]))]}
    if edges!=expected:
        raise ValueError('As quatro arestas nao fecham o retangulo do cupom')
    if abs((xs[1]-xs[0])-90)>0.05 or abs((ys[1]-ys[0])-24)>0.05:
        raise ValueError('Dimensao do cupom nao corresponde a 90x24mm')
    bx0,by0,bx1,by1=struct.unpack_from('<ffff',raw,8)
    if any(abs(a-b)>0.001 for a,b in zip((bx0,by0,bx1,by1),(xs[0],ys[0],xs[1],ys[1]))):
        raise ValueError('Bounding box e contorno divergentes')
    return tuple((xs[0],ys[0],xs[1],ys[1]))

def raster_rectangle(bbox,pitch_x,pitch_y,screen_x,screen_y):
    x0,y0,x1,y1=bbox
    def edges(a,b,pitch,offset,maxpix):
        start=math.ceil((a+offset)/pitch-0.5)
        end=math.ceil((b+offset)/pitch-0.5)
        if not (0<=start<end<=maxpix): raise ValueError('Limites fora do LCD')
        return start,end
    left,right=edges(x0,x1,pitch_x,screen_x/2,W)
    top,bottom=edges(y0,y1,pitch_y,screen_y/2,H)
    segments=[]
    for y in range(H):
        if top<=y<bottom:
            segments.extend(((left,0),(right-left,15),(W-right,0)))
        else:
            segments.append((W,0))
    encoded=encode_runs(segments)
    observed=inspect_rle(encoded)
    if observed!=(left,top,right,bottom,(right-left)*(bottom-top)):
        raise AssertionError(f'Mascara raster inesperada {observed}')
    return encoded,observed

def main():
    z,layers,profile=validate_archive(SRC)
    try:
        if profile['image_codecs']!=['pwszimg'] or len(layers)!=80:
            raise ValueError('Esperadas 80 camadas vetoriais; arquivo fora do cupom')
        all_raw=[z.read(layers[i][0]) for i in range(len(layers))]
        rectangles=[parse_rectangle_vector(raw) for raw in all_raw]
        if any(rect!=rectangles[0] for rect in rectangles):
            raise ValueError('Camadas do cupom nao identicas')
        cfg=json.loads(z.read('anycubic_photon_resins.pwsp'))
        machine=cfg['machine_type']
        pixel_x,pixel_y=profile['pixel_pitch_mm']
        screen_x,screen_y=machine['print_xsize'],machine['print_ysize']
        encoded,bounds=raster_rectangle(rectangles[0],pixel_x,pixel_y,screen_x,screen_y)
        with zipfile.ZipFile(OUT,'w') as dest:
            for item in z.infolist():
                name=item.filename
                if name.startswith('layer_images/layer_') and name.endswith('.pwszImg'):
                    name=name.replace('.pwszImg','.pw0Img')
                    dest.writestr(name,encoded,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
                else:
                    dest.writestr(item.filename,z.read(item.filename),compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
        oz,olayers,oprofile=validate_archive(OUT)
        try:
            if oprofile['image_codecs']!=['pw0img']:
                raise ValueError('Codigo PW0 nao validado no arquivo de saida')
            if set(z.namelist())-set(oz.namelist()) != {f'layer_images/layer_{i}.pwszImg' for i in range(80)}:
                raise ValueError('Arquivos originais extras inesperados')
            for original_name in z.namelist():
                if original_name.endswith('.pwszImg'):
                    continue
                if oz.read(original_name)!=z.read(original_name):
                    raise ValueError(f'Alteracao de metadados proibida: {original_name}')
            if any(oz.read(f'layer_images/layer_{i}.pw0Img')!=encoded for i in range(80)):
                raise ValueError('Falhou comparacao raster PW0 em todas as camadas')
            if oz.testzip() is not None:
                raise ValueError('ZIP invalido')
        finally:
            oz.close()
        report={'fonte':SRC.name,'sha256_fonte':sha256_file(SRC),
            'arquivo_controle':OUT.name,'sha256_controle':sha256_file(OUT),
            'status':'CONVERSAO EXPERIMENTAL; NAO VALIDADA EM WORKSHOP OU PRINTER REAL',
            'perfil':profile,'bbox_vetorial_mm':rectangles[0],
            'pixel_interval_x_y':bounds[:4], 'pixel_area':bounds[4],
            'dimensoes_raster_mm':[(bounds[2]-bounds[0])*pixel_x,(bounds[3]-bounds[1])*pixel_y],
            'camadas_convertidas':80,
            'metadados_inalterados':True,
            'limites':'Reamostragem do vetor para pixels inteiros pode diferir do rasterizador interno da impressora por 1 pixel. Firmware nao testado.'}
        REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps(report,ensure_ascii=False,indent=2))
    finally:
        z.close()

if __name__=='__main__': main()
