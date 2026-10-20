"""Exploratory check of stronger current-execution equivalence.

Records actual action sequences on the frozen training traces, then checks
uniform no-wrap edit transitions for parents with identical full action traces.
No search method is retuned and no held-out score is used.
"""
import collections
import hashlib
import itertools
import json
from pathlib import Path
import time

import pilot

start=time.perf_counter()
OUT=pilot.OUT
bank=json.loads((OUT/'bank.json').read_text())
traces=json.loads((OUT/'traces.json').read_text())['train']
groups=collections.defaultdict(list)
fingerprints={}
for p,g in enumerate(pilot.GENOMES):
    decisions=[]
    for t in traces:
        rem=[]
        for item in t['items']:
            chosen=pilot.select(g,rem,item)
            decisions.append(chosen)
            if chosen==-1:rem.append(pilot.CAP-item)
            else:rem[chosen]-=item
    signature=tuple(decisions)
    groups[signature].append(p)
    fingerprints[p]=hashlib.sha256(json.dumps(decisions).encode()).hexdigest()
def neighbor(p,j,d):
    g=list(pilot.GENOMES[p]);g[j]+=d
    return pilot.IDS[tuple(g)] if -2<=g[j]<=2 else None
kernel={}
for p in range(len(pilot.GENOMES)):
    kernel[p]=collections.Counter(tuple(bank['train_bins'][q]) for j in range(4) for d in (-1,1) if (q:=neighbor(p,j,d)) is not None)
total=bad=0
witness=None
for members in groups.values():
    for p,q in itertools.combinations(members,2):
        total+=1
        kp,kq=kernel[p],kernel[q];np=sum(kp.values());nq=sum(kq.values())
        tv=sum(abs(kp[x]/np-kq[x]/nq) for x in kp.keys()|kq.keys())/2
        if tv>1e-12:
            bad+=1
            if witness is None:witness={'p':p,'q':q,'p_genome':pilot.GENOMES[p],'q_genome':pilot.GENOMES[q],'action_sha256':fingerprints[p],'kernel_tv':tv}
result={'scope':'Post-pilot exploratory; same frozen training traces; no test access or search tuning',
        'behavior_cells':len(groups),'pairs_with_same_full_training_actions':total,
        'same_action_pairs_different_next_performance_kernel':bad,'fraction':bad/total,
        'witness':witness,'extra_candidate_trace_evaluations':len(pilot.GENOMES)*len(traces),
        'wall_seconds':time.perf_counter()-start,'action_hashes':fingerprints}
(OUT/'behavior_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
public={k:v for k,v in result.items() if k!='action_hashes'}
print(json.dumps(public,indent=2))
