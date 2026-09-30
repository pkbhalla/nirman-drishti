"""Builds a labelled stress-test set from SYNTHETIC habitations: clear / dialect-drift / adversarial."""
import random
def drift(name,rnd):
    n=name.lower()
    ops=[lambda s:s+"wa", lambda s:s.replace("b","v") if "b" in s else s+"a", lambda s:s.replace("v","b"),
         lambda s:s.replace("a","aa",1), lambda s:s.replace("ph","f"), lambda s:s[:-2] if len(s)>6 else s+"wa"]
    return rnd.choice(ops)(n).capitalize()
def build(habs,block_ids,n_each=20,seed=5):
    rnd=random.Random(seed); out=[]; i=0
    names=habs.groupby("BLOCK_ID").HAB_NAME.apply(list).to_dict(); b2n={v:k for k,v in block_ids.items()}
    def pick():
        r=habs.iloc[rnd.randrange(len(habs))]; return r
    for _ in range(n_each):
        r=pick(); i+=1; out.append(dict(id=i,stratum="clear",block=b2n[r.BLOCK_ID],mention=r.HAB_NAME,expected_hab_id=int(r.HAB_ID)))
    for _ in range(n_each):
        r=pick(); i+=1; out.append(dict(id=i,stratum="dialect",block=b2n[r.BLOCK_ID],mention=drift(r.HAB_NAME,rnd),expected_hab_id=int(r.HAB_ID)))
    for k in range(n_each):
        r=pick(); i+=1
        if k%2==0: out.append(dict(id=i,stratum="adversarial",block=b2n[r.BLOCK_ID],mention="",expected_hab_id=None))
        else: out.append(dict(id=i,stratum="adversarial",block=b2n[r.BLOCK_ID],mention="Xqzt"+str(k),expected_hab_id=None))
    return out
