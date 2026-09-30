import pandas as pd
from .geo import nearest_line
from .extract import extract, gemini_arbiter
from .resolver import resolve

def enrich_habitations(habs,lines,radius_m=500):
    """dist_road_m = distance to nearest line in `lines`. NOTE: pass EXISTING roads for a true connectivity test;
    sanctioned-proposal lines alone only tell you which habitations have a pending proposal."""
    d=[nearest_line((r.lon,r.lat),lines,radius_m=radius_m*6)[1] for r in habs.itertuples()]
    h=habs.copy(); h["dist_to_line_m"]=d; return h

def handle(text=None,audio=None,mime="audio/ogg",habs=None,block_ids=None):
    """block_ids: {block_name: OMMAS BLOCK_ID}. Returns dict with extraction + resolution."""
    ex=extract(text,audio,mime,blocks=list(block_ids))
    blk=ex.get("detected_block")
    if blk not in block_ids:
        return dict(extraction=ex,resolution=dict(status="ABSTAIN",reason="block not identified",candidates=[]),
                    follow_up="Kripya apna block batayein.")
    res=resolve(ex.get("village_mention_latin") or "",block_ids[blk],habs,arbiter=gemini_arbiter)
    out=dict(extraction=ex,resolution=res.__dict__)
    if res.status=="ABSTAIN":
        names=", ".join(c["name"] for c in res.candidates) or "-"
        out["follow_up"]=f"Gaon ka naam saaf nahi hai. Kya aapka gaon inme se hai: {names}?"
    return out
