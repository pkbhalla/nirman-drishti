"""Build demo priorities from SYNTHETIC data -> data/priorities_demo.csv"""
import sys, os
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
import random, pandas as pd
from nirman_drishti import synthetic
from nirman_drishti.pipeline import enrich_habitations
from nirman_drishti.scoring import priority
habs,meta,lines=synthetic.make()
h=enrich_habitations(habs,lines).rename(columns={"dist_to_line_m":"dist_road_m"})
h["sanctioned"]=h.dist_road_m<=500
rnd=random.Random(3)
loud=h[h.block.isin(["Niyamtabad","Chandauli"])].HAB_ID.tolist()
quiet=h[h.block.isin(["Naugarh"])].HAB_ID.tolist()
reqs=[rnd.choice(loud[:15]) for _ in range(120)]+[rnd.choice(quiet) for _ in range(6)]   # loud plains vs quiet remote block
p=priority(h,pd.DataFrame({"hab_id":reqs}))
p.drop(columns=[c for c in p.columns if c=="STATE_ID"]).to_csv("data/priorities_demo.csv",index=False)
print(p.attrs["weights_used"]); print(p.head(8)[["HAB_NAME","block","TOT_POPULA","requests","priority"]])
print(p.groupby("block").priority.mean().round(1).sort_values(ascending=False))
