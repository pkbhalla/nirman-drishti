"""Pure-python geometry: metres via local equirectangular projection, point-to-polyline distance."""
import math
R=6371008.8
def _xy(lon,lat,lat0): 
    return (math.radians(lon)*R*math.cos(math.radians(lat0)), math.radians(lat)*R)
def point_segment_m(p,a,b):
    lat0=p[1]; px,py=_xy(*p,lat0); ax,ay=_xy(*a,lat0); bx,by=_xy(*b,lat0)
    dx,dy=bx-ax,by-ay; L=dx*dx+dy*dy
    t=0 if L==0 else max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L))
    return math.hypot(px-(ax+t*dx),py-(ay+t*dy))
def point_line_m(p,line):
    return min(point_segment_m(p,line[i],line[i+1]) for i in range(len(line)-1)) if len(line)>1 else float("inf")
def nearest_line(p,lines,radius_m=None):
    """lines: list of (id,[(lon,lat),...]). Returns (id,dist_m) or (None,inf). Cheap bbox prefilter."""
    best=(None,float("inf"))
    for lid,ln in lines:
        if radius_m:
            pad=radius_m/111000*1.5
            xs=[c[0] for c in ln]; ys=[c[1] for c in ln]
            if p[0]<min(xs)-pad or p[0]>max(xs)+pad or p[1]<min(ys)-pad or p[1]>max(ys)+pad: continue
        d=point_line_m(p,ln)
        if d<best[1]: best=(lid,d)
    return best
