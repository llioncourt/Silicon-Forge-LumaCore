#!/usr/bin/env python3
"""Creates a single contiguous solid wedge for cure/optical coupon studies.
Additional deps for this authoring-only script: trimesh, shapely.
"""
from pathlib import Path
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import triangulate

out=Path(__file__).parent/'CUPOM_CALIBRACAO_UMA_PECA.stl'
outline=[(-45,0),(45,0),(45,10),(25,10),(25,8),(5,8),(5,6),(-15,6),(-15,4),(-35,4),(-35,2),(-45,2)]
p=Polygon(outline)
assert p.is_valid
tris=[t for t in triangulate(p) if p.covers(t.representative_point()) and p.covers(t)]
verts=[]; lookup={}; faces=[]
def v(x,y,z):
    key=(float(x),float(y),float(z))
    if key not in lookup:
        lookup[key]=len(verts); verts.append(key)
    return lookup[key]
for tri in tris:
    xyz=np.array(tri.exterior.coords)[:3]
    faces.append([v(x,-12,z) for x,z in xyz])
    faces.append([v(x,12,z) for x,z in xyz[::-1]])
for a,b in zip(outline,outline[1:]+outline[:1]):
    ax,az=a;bx,bz=b
    a0=v(ax,-12,az);a1=v(ax,12,az);b0=v(bx,-12,bz);b1=v(bx,12,bz)
    faces.extend([[a0,b0,b1],[a0,b1,a1]])
m=trimesh.Trimesh(vertices=verts,faces=faces,process=True)
m.fix_normals()
assert m.is_watertight and m.is_volume and len(m.split())==1
m.export(out)
print(out)
