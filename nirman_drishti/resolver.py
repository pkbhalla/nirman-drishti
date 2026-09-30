"""Resolve a spoken village/habitation mention to a HAB_ID inside one OMMAS block, or ABSTAIN.
Deterministic candidate generation; optional Gemini only arbitrates among the shortlist."""
from dataclasses import dataclass, field
import pandas as pd
from .phonetic import rank

ACCEPT=0.80   # minimum top score
MARGIN=0.08   # minimum gap to runner-up

@dataclass
class Resolution:
    status:str                      # RESOLVED | ABSTAIN
    hab_id:int|None=None
    name:str|None=None
    score:float=0.0
    candidates:list=field(default_factory=list)   # [{hab_id,name,population,score}]
    reason:str=""

def resolve(mention:str, block_id:int, habs:pd.DataFrame, arbiter=None)->Resolution:
    if not mention or not mention.strip():
        return Resolution("ABSTAIN",reason="no village mentioned")
    pool=habs[habs.BLOCK_ID==block_id].reset_index(drop=True)
    if pool.empty: return Resolution("ABSTAIN",reason="unknown block")
    r=rank(mention,list(pool.HAB_NAME),top=3)
    cands=[dict(hab_id=int(pool.HAB_ID[i]),name=pool.HAB_NAME[i],population=int(pool.TOT_POPULA[i]),score=round(s,3)) for i,s in r]
    top=cands[0]; second=cands[1]["score"] if len(cands)>1 else 0.0
    dup=[c for c in cands if c["name"].strip().lower()==top["name"].strip().lower()]
    if len(dup)>1:
        return Resolution("ABSTAIN",candidates=cands,reason="same habitation name appears more than once in block")
    if top["score"]<ACCEPT:
        return Resolution("ABSTAIN",candidates=cands,reason="low similarity")
    if top["score"]-second<MARGIN:
        if arbiter:
            pick=arbiter(mention,cands)
            if pick is not None:
                c=next(c for c in cands if c["hab_id"]==pick)
                return Resolution("RESOLVED",c["hab_id"],c["name"],c["score"],cands,"arbiter")
        return Resolution("ABSTAIN",candidates=cands,reason="ambiguous between close candidates")
    return Resolution("RESOLVED",top["hab_id"],top["name"],top["score"],cands,"deterministic")
