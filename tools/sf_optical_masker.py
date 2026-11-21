#!/usr/bin/env python3
"""Silicon Forge | experimental volumetric exposure-field processor (M7 Pro).

Works on already sliced 8-bit gray PNG layers. Never changes black pixels or mesh outline.
Emits PNG images for INDEPENDENT inspection / controlled material calibration ONLY.
Does not produce machine-native pwsz, and is NOT calibrated for any resin/firmware.

No completely-off internal pixels: minimum factor 0.92 by default.

Requires: numpy, opencv-python-headless, Pillow. Local venv is recommended.
"""
from __future__ import annotations
import argparse, hashlib, json, math, os, re, sys, time
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

WIDTH, HEIGHT = 13312, 5120
PITCH_X, PITCH_Y = 223.64 / WIDTH, 126.48 / HEIGHT

def grad_field(x: np.ndarray, y: np.ndarray, z: float) -> np.ndarray:
    """Experimental guide/extraction DOSE intent; not refractive-index prediction."""
    field = np.zeros((len(y), len(x)), np.float32)
    X = x[np.newaxis, :]
    Y = y[:, np.newaxis]
    def bump(amp, xc, yc, rx, ry, zlo, zhi, fade=5.0):
        nonlocal field
        if z < zlo or z > zhi:
            return
        entry = min(1.0, max(0.0, (z-zlo)/fade))
        exit_ = min(1.0, max(0.0, (zhi-z)/fade))
        ramp = (entry*entry*(3-2*entry))*(exit_*exit_*(3-2*exit_))
        if ramp <= 0: return
        field += (amp*ramp*np.exp(-0.5*((X-xc)/rx)**2 -0.5*((Y-yc)/ry)**2)).astype(np.float32)
    cx = -4.0 + 4.0*math.sin((z-55)*0.031)
    cy = -2.0 + 3.0*math.sin((z-55)*0.023)
    bump(.48, cx, cy, 8.0, 7.5, 25, 137, 12)
    bump(.70, -5, -1, 11, 9, 97, 132, 6)
    bump(.35, 8, 2, 11, 7, 105, 134, 5)
    bump(.45, -2, 2, 5.5, 5, 126, 147, 5)
    bump(.40, -25, 1, 15, 6, 109, 137, 6)
    bump(.40,  29, 1, 16, 6, 109, 140, 6)
    bump(.28, -49, 1, 12, 5, 111, 134, 5)
    bump(.28,  50, 1, 12, 5, 113, 137, 5)
    if 101 <= z <= 144:
        sx=np.clip(np.cos((X/1.6 + z*.014)*2*np.pi),0,1)**8
        sy=np.clip(np.cos((Y/1.6 - z*.011)*2*np.pi),0,1)**8
        micro=(sx*sy).astype(np.float32)
        field=np.minimum(field,.83)+.17*micro*np.minimum(1., field*2.)
    return np.clip(field,0.,1.)

def modify_gray(img: np.ndarray, z_mm: float, reduction: float=.08,
                guard_mm: float=1.5, origin_x: float=0., origin_y: float=0.,
                pitch_x: float=PITCH_X, pitch_y: float=PITCH_Y,
                center_px: tuple[float,float] | None=None,
                profile: str='statue') -> tuple[np.ndarray,dict]:
    """Apply grayscale only to solid pixels well INSIDE source model silhouette."""
    if img.ndim!=2 or img.dtype!=np.uint8: raise ValueError('expected 8bit gray PNG')
    if not 0 <= reduction <= 0.10: raise ValueError('conservative reduction 0..0.10 only')
    h,w=img.shape
    out=img.copy()
    positive=img>192
    ys,xs=np.where(positive)
    if not len(xs): return out, dict(pixels_changed=0, dose_min=1.0, z_mm=z_mm)
    left,right=int(xs.min()),int(xs.max())+1
    top,bottom=int(ys.min()),int(ys.max())+1
    roi=positive[top:bottom,left:right].astype(np.uint8)
    dist=cv2.distanceTransform(roi, cv2.DIST_L2, 5)
    safe=(dist*min(pitch_x,pitch_y) >= guard_mm)
    if center_px is None: center_px=((w-1)/2,(h-1)/2)
    cx,cy=center_px
    col_x=(np.arange(left,right,dtype=np.float32)-cx)*pitch_x-origin_x
    count=0; min_multiplier=1.0
    for start in range(0, bottom-top, 128):
        stop=min(bottom-top,start+128)
        rows=np.arange(top+start,top+stop,dtype=np.float32)
        row_y=(cy-rows)*pitch_y-origin_y
        safe_tile=safe[start:stop,:]
        if not safe_tile.any(): continue
        if profile=='statue':
            field=grad_field(col_x,row_y,z_mm)
        elif profile=='coupon':
            if z_mm <= 1.0:continue
            strengths=np.clip(np.floor((col_x+45.0)/18.0),0,4).astype(np.float32)*.25
            field=np.broadcast_to(strengths[None,:], (len(row_y),len(col_x)))
        else:raise ValueError('unknown profile: '+profile)
        if not np.any(field):continue
        ratio=1.0-reduction*field
        source=img[top+start:top+stop,left:right]
        target=np.rint(source*ratio).astype(np.uint8)
        mask=safe_tile & (target < source)
        if mask.any():
            out_tile=out[top+start:top+stop,left:right]
            out_tile[mask]=target[mask]
            count+=int(mask.sum())
            min_multiplier=min(min_multiplier,float(ratio[mask].min()))
    assert np.all(out[img==0]==0)
    assert np.all(out[img>0]>0)
    assert np.all(out<=img)
    return out,dict(pixels_changed=count,dose_min=round(min_multiplier,6),z_mm=round(z_mm,4),
                    valid_original_exposure_pixels=int(positive.sum()),
                    pct_modified_original=round(100*count/max(1,int(positive.sum())),3),
                    png_size_px=[w,h])

def process_folder(args):
    src=Path(args.input_dir); dst=Path(args.output_dir)
    if not src.is_dir(): raise SystemExit('ERROR: input directory does not exist')
    dst.mkdir(parents=True,exist_ok=True)
    images=sorted(src.glob('*.png'),key=lambda p:[int(s) if s.isdigit() else s.lower() for s in re.split(r'(\d+)',p.name)])
    if not images: raise SystemExit('ERROR: no PNG files in folder')
    results=[]
    for number,path in enumerate(images):
        digits=re.findall(r'\d+',path.stem)
        index=int(digits[-1]) if digits else number
        z=args.z0_mm+(index+args.index_offset)*args.layer_mm
        original=np.array(Image.open(path).convert('L'))
        if original.shape!=(HEIGHT,WIDTH) and not args.allow_nonstandard:
            raise RuntimeError(f'{path.name}: size {original.shape[::-1]} != official M7 Pro {WIDTH}x{HEIGHT}')
        transformed,stats=modify_gray(original,z,args.reduction,args.guard_mm,args.origin_x_mm,args.origin_y_mm,
                 PITCH_X,PITCH_Y,profile=args.profile)
        savepath=dst/path.name
        Image.fromarray(transformed).save(savepath, optimize=True)
        stats.update(file=path.name,sha256_original=hashlib.sha256(path.read_bytes()).hexdigest())
        results.append(stats)
        print(path.name,'z=',round(z,2),'changed=',stats['pixels_changed'],flush=True)
    with open(dst/'AUDITORIA.json','w',encoding='utf-8') as fp:
        json.dump(dict(config=vars(args),invariants='exterior unchanged; zero->zero; no lit pixel becomes dark',
                       layers=results),fp,indent=2,ensure_ascii=False,default=str)

def main():
    p=argparse.ArgumentParser(description='SF M7 Pro experimental grayscale guides. NOT a printer file.')
    p.add_argument('--input-dir',required=True,help='8-bit PNG sliced exposures, do NOT use JPG')
    p.add_argument('--output-dir',required=True,help='new folder to hold derived images')
    p.add_argument('--layer-mm',type=float,default=.05)
    p.add_argument('--z0-mm',type=float,default=0.0)
    p.add_argument('--index-offset',type=int,default=0)
    p.add_argument('--reduction',type=float,default=.08)
    p.add_argument('--guard-mm',type=float,default=1.5)
    p.add_argument('--profile',choices=['statue','coupon'],default='statue')
    p.add_argument('--origin-x-mm',type=float,default=0.0)
    p.add_argument('--origin-y-mm',type=float,default=0.0)
    p.add_argument('--allow-nonstandard',action='store_true')
    args=p.parse_args()
    process_folder(args)

if __name__=='__main__': main()
