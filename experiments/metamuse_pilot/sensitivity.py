"""Post-outcome robustness analysis; not a pre-registered confirmation.

Uses the frozen bank, with no extra program evaluations or method tuning.
Checks whether uniform mutation-kernel aliasing persists after positive-scaling
canonicalization and without wraparound. Also summarizes existing learning curves.
"""
import collections
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'
bank=json.loads((OUT/'bank.json').read_text())
genomes=[tuple(x) for x in bank['genomes']]
ids={g:i for i,g in enumerate(genomes)}
def norm(g):
    v=math.gcd(*[abs(x) for x in g])
    return tuple(x//v for x in g) if v else g
canonical=[i for i,g in enumerate(genomes) if norm(g)==g]
def neighbors(p,op):
    g=genomes[p]
    result=[]
    if op=='coordinate_no_wrap':
        for j in range(4):
            for direction in (-1,1):
                h=list(g);h[j]+=direction
                if -2<=h[j]<=2: result.append(ids[tuple(h)])
    elif op=='sign_flip':
        for j in range(4):
            h=list(g);h[j]=-h[j];result.append(ids[tuple(h)])
    return result
def audit(pool,op):
    groups=collections.defaultdict(list)
    for p in pool:groups[tuple(bank['train_bins'][p])].append(p)
    # Destination classes include every generated policy, not only the parent subset.
    kernels={p:collections.Counter(tuple(bank['train_bins'][q]) for q in neighbors(p,op)) for p in pool}
    total=bad=0;best=None;max_tv=-1
    for members in groups.values():
        for p,q in itertools.combinations(members,2):
            kp,kq=kernels[p],kernels[q];np=sum(kp.values());nq=sum(kq.values())
            tv=sum(abs(kp[x]/np-kq[x]/nq) for x in kp.keys()|kq.keys())/2
            total+=1;bad+=tv>1e-12
            if tv>max_tv:max_tv=tv;best=[p,q]
    return {'parents':len(pool),'aliased_pairs':total,'different_kernel_pairs':bad,'fraction':bad/total if total else None,'max_tv':max_tv,'witness_ids':best}
res={'scope':'Exploratory, added after frozen pilot; no new fitness evaluations or tuning',
     'operator_audits':{f'{subset}_{op}':audit(pool,op) for subset,pool in [('all',range(len(genomes))),('canonical',canonical)] for op in ('coordinate_no_wrap','sign_flip')}}
rows=list(csv.DictReader((OUT/'search_history.csv').open()))
curves={}
for method in sorted({r['method'] for r in rows}):
    sub=[r for r in rows if r['method']==method]
    curves[method]={str(t):statistics.mean(float(r['best_score']) for r in sub if int(r['attempt'])==t) for t in (24,48,72,120)}
res['mean_best_training_score_at_attempt']=curves
(OUT/'sensitivity.json').write_text(json.dumps(res,indent=2),encoding='utf-8')
# Preserve frozen original hashes; this separate manifest covers the new analysis.
hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'sensitivity.py',OUT/'sensitivity.json')}
(OUT/'sensitivity_hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
print(json.dumps(res,indent=2))
