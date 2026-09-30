"""Equity-weighted priority: P = w1*demand_intensity + w2*deficit + w3*vulnerability.
Each component is rank-normalised to 0..1 across habitations so no single scale dominates.
Missing components are dropped and weights renormalised; the result reports which were used."""
import numpy as np, pandas as pd

DEFAULT_W=dict(demand=0.25,deficit=0.45,vulnerable=0.30)

def _rank01(s):
    return s.rank(pct=True) if s.notna().any() else s

def priority(habs:pd.DataFrame, requests:pd.DataFrame, weights=None, radius_m=500):
    """habs cols: HAB_ID,HAB_NAME,TOT_POPULA,BLOCK_ID,[dist_road_m],[sanctioned],[vuln_ratio]
       requests cols: hab_id (resolved only)"""
    w=dict(weights or DEFAULT_W); h=habs.copy()
    cnt=requests.groupby("hab_id").size() if len(requests) else pd.Series(dtype=int)
    h["requests"]=h.HAB_ID.map(cnt).fillna(0)
    per1k=h.requests/(h.TOT_POPULA.clip(lower=50)/1000)          # per 1000 people, floor on tiny populations
    per1k=per1k.clip(upper=per1k.quantile(0.95) if per1k.max()>0 else 0)  # winsorise loud hotspots
    h["demand"]=_rank01(per1k)
    parts={}
    if "dist_road_m" in h and h.dist_road_m.notna().any():
        unconn=(h.dist_road_m>radius_m).astype(float)
        nosan=(~h.get("sanctioned",pd.Series(False,index=h.index)).astype(bool)).astype(float)
        pop=_rank01(h.TOT_POPULA)
        parts["deficit"]=(0.6*unconn+0.25*unconn*nosan+0.15*pop).clip(0,1)
    if "vuln_ratio" in h and h.vuln_ratio.notna().any(): parts["vulnerable"]=_rank01(h.vuln_ratio)
    parts["demand"]=h["demand"]
    used={k:w[k] for k in parts}; tot=sum(used.values())
    h["priority"]=sum(parts[k]*used[k]/tot for k in parts)*100
    for k,v in parts.items(): h["c_"+k]=v
    h.attrs["weights_used"]={k:round(v/tot,3) for k,v in used.items()}
    return h.sort_values("priority",ascending=False)
