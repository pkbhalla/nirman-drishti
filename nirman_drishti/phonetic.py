"""Deterministic phonetic matching for Purvanchali/Bhojpuri-drifted place names (Latin script)."""
import re
from difflib import SequenceMatcher

def norm(s:str)->str:
    return re.sub(r"[^a-z ]","",(s or "").lower().strip())

def key(s:str)->str:
    """Phonetic key: b/v/w merge, ph->f, z->j, doubles collapsed, inner vowels dropped, final 'wa'/'a' stripped."""
    t=norm(s).replace(" ","")
    if not t: return ""
    t=re.sub(r"(wa|va|ua)$","",t)
    t=t.replace("ph","f").replace("sh","s").replace("kh","k").replace("gh","g").replace("ch","c").replace("th","t").replace("dh","d").replace("bh","b")
    t=t.replace("w","b").replace("v","b").replace("z","j").replace("y","i")
    t=re.sub(r"(.)\1+",r"\1",t)
    t=t[0]+re.sub(r"[aeiou]","",t[1:])
    return t

def similarity(a:str,b:str)->float:
    ka,kb=key(a),key(b)
    k=SequenceMatcher(None,ka,kb).ratio() if ka and kb else 0.0
    r=SequenceMatcher(None,norm(a),norm(b)).ratio()
    return max(k*0.95,r)

def rank(mention:str,names:list,top:int=3):
    """Return [(index,score)] best first."""
    sc=sorted(((i,similarity(mention,n)) for i,n in enumerate(names)),key=lambda x:-x[1])
    return sc[:top]
