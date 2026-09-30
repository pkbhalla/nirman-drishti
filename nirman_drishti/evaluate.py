import statistics
def wilson(k,n,z=1.96):
    if n==0: return (0.0,0.0)
    p=k/n; d=1+z*z/n; m=p+z*z/(2*n); s=z*((p*(1-p)/n+z*z/(4*n*n))**.5); return ((m-s)/d,(m+s)/d)
def evaluate(samples,preds):
    """preds: {id:{hab_id|None, abstain:bool}}. Separates wrong answers, false abstains, hallucinated matches."""
    res={}
    for st in ["ALL"]+sorted({s["stratum"] for s in samples}):
        S=[s for s in samples if st=="ALL" or s["stratum"]==st]
        c=dict(correct=0,wrong=0,false_abstain=0,correct_abstain=0,hallucinated=0)
        for s in S:
            p=preds.get(s["id"],{"abstain":True}); ab=p.get("abstain",True) or p.get("hab_id") is None; t=s["expected_hab_id"]
            if t is None: c["correct_abstain" if ab else "hallucinated"]+=1
            elif ab: c["false_abstain"]+=1
            elif p["hab_id"]==t: c["correct"]+=1
            else: c["wrong"]+=1
        n=len(S); ans=c["correct"]+c["wrong"]+c["hallucinated"]; resolvable=sum(1 for s in S if s["expected_hab_id"] is not None)
        res[st]=dict(n=n,**c,precision_when_answered=(c["correct"]/ans if ans else None),
                     coverage_on_resolvable=(c["correct"]/resolvable if resolvable else None),
                     wilson95_precision=wilson(c["correct"],ans))
    return res
def spread(scores):
    q=statistics.quantiles(scores,n=4); d=statistics.quantiles(scores,n=10); m=statistics.mean(scores)
    return dict(n=len(scores),cv=statistics.pstdev(scores)/m if m else None,iqr=q[2]-q[0],p90_minus_p10=d[-1]-d[0])
