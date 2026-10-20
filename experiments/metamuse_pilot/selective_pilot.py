"""Collision-triggered matched-edit probes, independently frozen second bank.

Novelty is a research hypothesis. All probes and repeats consume equal budget.
Coin baseline has the same diagnostic action at collisions but randomizes the
retention decision; neutral drift avoids diagnostic expense entirely.
"""
import csv
import hashlib
import json
from pathlib import Path
import random
import statistics
import time

import pilot

ROOT=Path(__file__).resolve().parent
CFG=json.loads((ROOT/'selective_config.json').read_text())
OUT=ROOT/'selective_results_corrected'
OUT.mkdir(exist_ok=True)

def run(method,seed,scores):
    rng=random.Random(seed)
    records={}
    archive=[]
    rows=[]
    seen=set()
    best=None
    def value(p):return statistics.mean(records[p]['score'])
    def evaluate(p,role):
        nonlocal best
        assert len(rows)<CFG['evaluation_budget']
        records[p]={'score':scores[p]}
        seen.add(p)
        if best is None or (value(p),p)<(value(best),best):best=p
        rows.append({'method':method,'seed':seed,'attempt':len(rows)+1,'policy':p,'role':role,'best_policy':best,'best_score':value(best)})
        return scores[p]
    def signature(p):return tuple(records[p]['score'])
    def regular(p):
        return pilot.choose_archive(archive+[p],records,'performance_flat',rng)
    def retain_neutral(p,q):
        pool=sorted(set(archive+[p]))
        if len(pool)<=CFG['archive_size']:return pool
        protected={p,q,min(pool,key=lambda x:(value(x),x))}
        removable=[x for x in pool if x not in protected]
        # Conventional redundancy rule: remove the least distinct current performer;
        # all geometry is based on visible feedback, never the precomputed bank.
        drop=min(removable,key=lambda x:(min(pilot.distance(records[x]['score'],records[y]['score']) for y in pool if x!=y),-value(x),-x))
        return [x for x in pool if x!=drop]
    for p in rng.sample(range(len(pilot.GENOMES)),CFG['initial_pool_size']):
        evaluate(p,'initial');archive.append(p)
    collisions=probed=admitted=0
    while len(rows)<CFG['evaluation_budget']:
        if method=='random':p=rng.randrange(len(pilot.GENOMES))
        else:p=pilot.mutation(rng.choice(archive),rng.randrange(8))
        evaluate(p,'primary')
        aliases=[q for q in archive if q!=p and signature(q)==signature(p)]
        if aliases:
            collisions+=1
            q=min(aliases)
            if method=='neutral_drift':
                # Re-visiting an already active policy must not shrink the archive.
                if p not in archive:
                    archive=[x for x in archive if x!=q]+[p]
                archive=sorted(set(archive))
                assert len(archive)==CFG['archive_size']
                continue
            if method in ('selective_response','collision_coin') and len(rows)+4<=CFG['evaluation_budget']:
                probed+=1
                r1=[];r2=[]
                for label in CFG['probe_labels']:
                    r1.append(evaluate(pilot.mutation(p,label),'probe'))
                    r2.append(evaluate(pilot.mutation(q,label),'probe'))
                preserve=r1!=r2 if method=='selective_response' else rng.random()<0.5
                if preserve:
                    admitted+=1;archive=retain_neutral(p,q);continue
        if method!='random':archive=regular(p)
    return {'method':method,'seed':seed,'selected_policy':best,'train':value(best),
            'attempts':len(rows),'unique_evaluated':len(seen),
            'probe_attempts':sum(x['role']=='probe' for x in rows),
            'collisions':collisions,'probed_collisions':probed,'split_admissions':admitted},rows

def main():
    start=time.perf_counter()
    train=pilot.make_traces(CFG['train_seed'],False)
    test=pilot.make_traces(CFG['test_seed'],True)
    train_bins=[[pilot.pack(g,t['items']) for t in train] for g in pilot.GENOMES]
    test_bins=[[pilot.pack(g,t['items']) for t in test] for g in pilot.GENOMES]
    scores=[pilot.score(x,train) for x in train_bins]
    test_scores=[pilot.score(x,test) for x in test_bins]
    (OUT/'bank.json').write_text(json.dumps({'genomes':pilot.GENOMES,'train_bins':train_bins,'test_bins':test_bins,'train_scores':scores,'test_scores':test_scores}),encoding='utf-8')
    (OUT/'traces.json').write_text(json.dumps({'train':train,'test':test},indent=2),encoding='utf-8')
    runs=[];history=[]
    for seed in range(CFG['search_seeds']):
        for method in CFG['methods']:
            result,rows=run(method,seed,scores)
            result['test']=statistics.mean(test_scores[result['selected_policy']])
            runs.append(result);history.extend(rows)
    for name,rows in [('runs.csv',runs),('search_history.csv',history)]:
        with (OUT/name).open('w',newline='',encoding='utf-8') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    treatment=[r for r in runs if r['method']=='selective_response']
    summary={}
    for method in CFG['methods']:
        group=[r for r in runs if r['method']==method]
        diff=[t['test']-b['test'] for t,b in zip(treatment,group)]
        summary[method]={'mean_train':statistics.mean(r['train'] for r in group),
                         'mean_test':statistics.mean(r['test'] for r in group),
                         'mean_probes':statistics.mean(r['probe_attempts'] for r in group),
                         'mean_split_admissions':statistics.mean(r['split_admissions'] for r in group),
                         'treatment_minus_baseline_test':statistics.mean(diff),
                         'treatment_wins_ties_losses':[sum(d<-1e-12 for d in diff),sum(abs(d)<=1e-12 for d in diff),sum(d>1e-12 for d in diff)]}
    report={'config':CFG,'methods':summary,'wall_seconds':time.perf_counter()-start,
            'actual_precomputation_candidate_trace_evaluations':len(pilot.GENOMES)*len(train+test),
            'charged_search_candidate_evaluations':sum(r['attempts'] for r in runs),
            'llm_calls':0,'llm_tokens':0,'paid_cost_usd':0}
    (OUT/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'selective_config.json',ROOT/'selective_pilot.py',ROOT/'pilot.py']+sorted(OUT.glob('*')) if p.name!='hashes.json'}
    (OUT/'hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
