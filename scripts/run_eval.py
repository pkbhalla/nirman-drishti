"""Stress-test the resolver. With SYNTHETIC data this measures the algorithm, not real-world accuracy.
For a real benchmark, replace data with your Chandauli habitation layer + 60 hand-labelled transcripts."""
import json, sys, os
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from nirman_drishti import synthetic, evalset
from nirman_drishti.resolver import resolve
from nirman_drishti.evaluate import evaluate
habs,_,_=synthetic.make(); bids={k:v[0] for k,v in synthetic.BLOCKS.items()}
S=evalset.build(habs,bids)
P={}
for s in S:
    r=resolve(s["mention"],bids[s["block"]],habs)
    P[s["id"]]=dict(hab_id=r.hab_id,abstain=r.status=="ABSTAIN")
res=evaluate(S,P)
print(json.dumps(res,indent=2,default=str))
json.dump(res,open("eval_results.json","w"),indent=2,default=str)
