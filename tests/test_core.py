import sys, os; sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from nirman_drishti.phonetic import similarity
from nirman_drishti.resolver import resolve
from nirman_drishti import synthetic
def test_dialect():
    assert similarity("Rampurwa","Rampur")>0.85
    assert similarity("Vishunpur","Bisunpur")>0.85
def test_abstain_empty():
    habs,_,_=synthetic.make(); assert resolve("",4285,habs).status=="ABSTAIN"
def test_resolve_exact():
    habs,_,_=synthetic.make(); r=habs.iloc[0]; assert resolve(r.HAB_NAME,int(r.BLOCK_ID),habs).hab_id==r.HAB_ID
