"""SYNTHETIC data in the exact GeoSadak schema (HAB_ID, BLOCK_ID, HAB_NAME, TOT_POPULA; proposals with MRL_ID lines).
Names/coords are invented near Chandauli for demo + stress-testing. NOT real survey data."""
import random, pandas as pd
BLOCKS={"Barahani":(4280,25.30,83.30),"Chahaniya":(4281,25.20,83.10),"Chakia":(4282,24.95,83.20),"Chandauli":(4283,25.27,83.27),
        "Dhanapur":(4284,25.35,83.45),"Naugarh":(4285,24.85,83.15),"Niyamtabad":(4286,25.20,83.35),"Sakaldiha":(4287,25.30,83.55),"Shahabganj":(4288,25.05,83.55)}
ROOTS=["Ram","Shiv","Hari","Bisun","Mahua","Bara","Chhota","Naya","Purana","Kanak","Dev","Sita","Gopal","Raja","Kala","Lal","Amar","Bhim","Kesar","Nim"]
SUFF=["pur","ganj","nagar","pura","garhi","tola","gaon","patti","dih","khurd","kalan","bari","pokhar","mau"]
def make(seed=11,per_block=60):
    rnd=random.Random(seed); rows=[]; hid=1000000
    for b,(bid,lat,lon) in BLOCKS.items():
        seen=set(); remote=b in("Naugarh","Chakia")
        while len([r for r in rows if r["BLOCK_ID"]==bid])<per_block:
            nm=rnd.choice(ROOTS)+rnd.choice(SUFF)
            if nm in seen: continue
            seen.add(nm); hid+=1
            spread=0.22 if remote else 0.10
            rows.append(dict(HAB_ID=hid,STATE_ID=33,DISTRICT_ID=345,BLOCK_ID=bid,HAB_NAME=nm.capitalize(),
              TOT_POPULA=int(rnd.lognormvariate(5.6,0.8)),lat=lat+rnd.uniform(-spread,spread),lon=lon+rnd.uniform(-spread,spread),block=b,
              vuln_ratio=min(0.95,max(0.05,rnd.gauss(0.45 if remote else 0.22,0.1)))))
    habs=pd.DataFrame(rows)
    lines=[]; meta=[]; mid=259000
    for r in habs.itertuples():
        dense=0.8 if r.block not in("Naugarh","Chakia") else 0.35
        if rnd.random()<dense:
            mid+=1; off=rnd.uniform(0.001,0.004) if rnd.random()<0.85 else rnd.uniform(0.02,0.05)
            lines.append((mid,[(r.lon+off,r.lat-0.01),(r.lon+off,r.lat+0.01)]))
            meta.append(dict(MRL_ID=mid,BLOCK_ID=r.BLOCK_ID,PROPOSED_L=2.2,WORK_NAME=f"Road to {r.HAB_NAME}",IMS_YEAR=rnd.choice([2021,2022,2023]),IMS_BATCH=1))
    return habs,pd.DataFrame(meta),lines
