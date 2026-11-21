#!/usr/bin/env python3
"""Monte Carlo ray transport through a watertight STL, with assumptions.
Entrance: virtual photons injected above LED cavity (ideal coupling).
Processes: Beer-Lambert absorption, Henyey-Greenstein bulk scattering, Fresnel.
Parametric model, NOT calibrated optical prediction.
Requires: vtk, numpy. Run with source STL as argument; output JSON path optional.
"""
import vtk, numpy as np, json, math, time, os, sys
from vtk.util.numpy_support import vtk_to_numpy

if len(sys.argv)<2: raise SystemExit("Usage: python simulate_optics.py path/to/model.stl [results.json]")
SOURCE=sys.argv[1]
OUTPUT=sys.argv[2] if len(sys.argv)>2 else "diagnostico_optico_simulacao.json"
r=vtk.vtkSTLReader();r.SetFileName(SOURCE);r.Update()
dec=vtk.vtkQuadricDecimation();dec.SetInputConnection(r.GetOutputPort());dec.SetTargetReduction(0.85);dec.Update()
poly=dec.GetOutput()
locator=vtk.vtkStaticCellLocator();locator.SetDataSet(poly);locator.BuildLocator()
pts=vtk_to_numpy(poly.GetPoints().GetData()).astype(np.float64)
triangles=vtk_to_numpy(poly.GetPolys().GetConnectivityArray()).reshape(-1,3)
tri=pts[triangles]
a=tri[:,1]-tri[:,0]; b=tri[:,2]-tri[:,0]
area=np.linalg.norm(np.cross(a,b),axis=1)/2
normals=np.cross(a,b);normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
center=tri.mean(axis=1)
ZONE_NAMES=['cristais_base','pernas','torso','cabeca_rosto_cabelo','bracos_maos','plinto_saida_inferior']
def zone(x,y,z):
    if z<=3: return 5
    if z<78: return 0
    if z<105: return 1
    if abs(x)>=30: return 4
    if z<128: return 2
    return 3
labels=np.array([zone(*xyz) for xyz in center], dtype=np.uint8)
areas={ZONE_NAMES[i]:round(float(np.sum(area[labels==i])),2) for i in range(6)}
p0=[0.,0.,0.];p1=[0.,0.,0.];xp=[0.,0.,0.];pc=[0.,0.,0.]
t=vtk.mutable(0.);sub=vtk.mutable(0);cid=vtk.mutable(0);cell=vtk.vtkGenericCell()

def surface_intersection(origin,direction):
    for j in range(3):
        p0[j]=float(origin[j])
        p1[j]=p0[j]+float(direction[j])*450.
    hit=locator.IntersectWithLine(p0,p1,1e-6,t,xp,pc,sub,cid,cell)
    return (np.array(xp,dtype=np.float64),int(cid)) if hit else None

def rand_hg(d,g,rng):
    u=rng.random()
    if abs(g)<1e-7: cost=2*u-1
    else:
        ratio=(1-g*g)/(1-g+2*g*u)
        cost=(1+g*g-ratio*ratio)/(2*g)
        cost=np.clip(cost,-1,1)
    sint=np.sqrt(max(0,1-cost*cost))
    phi=rng.uniform(0,2*np.pi)
    e=np.array([0.,0.,1.]) if abs(d[2])<.9 else np.array([1.,0.,0.])
    uvec=np.cross(d,e);uvec/=np.linalg.norm(uvec)
    vvec=np.cross(d,uvec)
    out=cost*d+sint*(np.cos(phi)*uvec+np.sin(phi)*vvec)
    return out/np.linalg.norm(out)

def sample_disk(rng):
    rho=29.0*np.sqrt(rng.random())
    phi=2*np.pi*rng.random()
    return np.array([-4.1084+rho*np.cos(phi),-1.6172+rho*np.sin(phi),-4.70])

def sample_lambertian(rng,max_angle_deg=90.):
    sinth=np.sqrt(np.sin(np.radians(max_angle_deg))**2*rng.random())
    phi=2*np.pi*rng.random()
    return np.array([sinth*np.cos(phi),sinth*np.sin(phi),np.sqrt(max(0,1-sinth*sinth))])

def fresnel_reflectance(cos_i,n1,n2):
    sin_t2=(n1/n2)**2*(1-cos_i*cos_i)
    if sin_t2>=1:return 1.
    ct=np.sqrt(max(0,1-sin_t2))
    rs=(n1*cos_i-n2*ct)/(n1*cos_i+n2*ct)
    rp=(n2*cos_i-n1*ct)/(n2*cos_i+n1*ct)
    return 0.5*(rs*rs+rp*rp)

def simulate(profile,angle_deg,mu_a,mu_s,photons=4000,seed=123):
    rng=np.random.default_rng(seed)
    counts=np.zeros(6,dtype=np.float64)
    path_lengths=[]; boundary_hits=0; emitted=0.; absorbed=0.; misses=0
    nres=1.5
    for idx in range(photons):
        pos=sample_disk(rng)
        d=sample_lambertian(rng,angle_deg)
        weight=1.;travel=0.
        for step in range(80):
            if weight<1e-3 or travel>600:break
            hit=surface_intersection(pos,d)
            if hit is None: misses+=1;break
            hitpos,hitidx=hit
            hitdist=np.linalg.norm(hitpos-pos)
            if hitdist<1e-5:
                pos=pos+d*0.003;continue
            scatter_dist=float('inf') if mu_s==0 else rng.exponential(1/mu_s)
            segment=min(hitdist,scatter_dist)
            next_weight=weight*np.exp(-mu_a*segment)
            absorbed+=weight-next_weight
            weight=next_weight;travel+=segment
            if scatter_dist<hitdist:
                pos=pos+d*segment
                d=rand_hg(d,0.75,rng)
                pos=pos+d*0.004
                continue
            n=normals[hitidx]
            dot=float(np.dot(d,n))
            if dot<0:n=-n;dot=-dot
            dot=min(1.,max(0.,dot))
            R=fresnel_reflectance(dot,nres,1.0)
            outgoing=weight*(1-R)
            counts[zone(*hitpos)]+=outgoing
            emitted+=outgoing
            weight*=R
            boundary_hits+=1
            if weight<1e-3:break
            d=d-2*dot*n
            d/=np.linalg.norm(d)
            pos=hitpos+d*0.004
        path_lengths.append(travel)
    return {'profile':profile,'half_angle_deg':angle_deg,'mu_a_1_per_mm':mu_a,
        'mu_s_1_per_mm':mu_s,'num_photons':photons,
        'emitted_fraction':round(float(emitted/photons),5),
        'absorbed_fraction':round(float(absorbed/photons),5),
        'avg_path_mm':round(float(np.mean(path_lengths)),2),
        'boundary_hits_per_photon':round(float(boundary_hits/photons),3),
        'numerical_misses':misses,
        'zones_energy_pct_of_source':{ZONE_NAMES[i]:round(float(counts[i]/photons*100),4) for i in range(6)},
        'zones_energy_per_area_relative':{ZONE_NAMES[i]:round(float((counts[i]/photons)/areas[ZONE_NAMES[i]]*10000),6) for i in range(6)}}

cases=[(name,angle,mu_a,mu_s)
       for mu_a,mu_s in [(0.005,0.0),(0.020,0.0),(0.020,0.015)]
       for name,angle in [('original_difuso',90),('feixe_45',45),('feixe_30',30),('feixe_15',15)]]
results=[]
for i,(name,angle,mu_a,mu_s) in enumerate(cases):
    rr=simulate(name,angle,mu_a,mu_s,photons=4000,seed=9827)
    results.append(rr)
    print(f"case {i+1}/{len(cases)} {name}: emitted={rr['emitted_fraction']:.3f}",flush=True)
model_assumptions={
 'source':'ideal uniform circular 58mm emitter virtual injection at z=-4.70 mm',
 'materials':'single homogeneous resin n=1.50 assumed, air n=1.00',
 'interfaces':'Fresnel boundary reflection and total internal reflection, Unipega not modeled',
 'absorption':'mu_a 0.005/0.020 per mm, hypothetical',
 'scattering':'mu_s 0/0.015 per mm, HG anisotropy g=0.75 hypothetical',
 'source_optics':'angle-limited Lambertian idealizations; no physical optics designed',
 'mesh':'85% triangle reduction from supplied watertight STL',
 'zones':'geometric bins, not fine semantic segmentation',
 'limitations':'no empirical resin/LED/coating calibration, no wavelength-resolved results'
}
with open(OUTPUT,'w',encoding='utf-8') as f:
    json.dump({'source_mesh':os.path.basename(SOURCE),'model_assumptions':model_assumptions,
               'surface_area_mm2':areas,'results':results},f,indent=2,ensure_ascii=False)
print("WROTE",OUTPUT)
