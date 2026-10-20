"""CPU-only study of proposal-conditioned archive information.

All generated policies are trusted coefficient tuples in a fixed grammar.
No model, embedding model, pickle input, arbitrary program or package is loaded.
The reviewed upstream Bin/BPPEval classes are AST-extracted only for conformance.
Search policies receive a masked feedback interface; precomputed test values are
never passed to search. Every probe/duplicate attempt is charged to the budget.
"""
from __future__ import annotations

import ast
import collections
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import random
import statistics
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / 'config.json').read_text())
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
COEFF = CFG['coefficients']
GENOMES = list(itertools.product(COEFF, repeat=4))
IDS = {g: i for i, g in enumerate(GENOMES)}
CAP = CFG['capacity']


def mutation(pid, label):
    """Eight labeled edits: increment/decrement one coefficient, with wrap."""
    g = list(GENOMES[pid])
    axis, direction = label // 2, 1 if label % 2 == 0 else -1
    g[axis] = COEFF[(COEFF.index(g[axis]) + direction) % len(COEFF)]
    return IDS[tuple(g)]


def select(g, remaining, item):
    a, b, c, d = g
    eligible = []
    nb = len(remaining)
    for i, rem in enumerate(remaining):
        if rem < item:
            continue
        r = (rem - item) / CAP
        score = a*r + b*r*r + c*(i+1)/(nb+1) + d*(r < 0.2)
        eligible.append((score, i))
    return min(eligible)[1] if eligible else -1


def pack(g, items):
    remaining = []
    for item in items:
        chosen = select(g, remaining, item)
        if chosen == -1:
            remaining.append(CAP-item)
        else:
            remaining[chosen] -= item
    assert all(0 <= r < CAP for r in remaining)
    assert CAP*len(remaining)-sum(remaining) == sum(items)
    return len(remaining)


def make_traces(seed, shifted):
    rng = random.Random(seed)
    traces = []
    n = CFG['items_per_trace']
    for family in ('uniform', 'weibull', 'complementary', 'phased'):
        for rep in range(CFG['traces_per_family']):
            if family == 'uniform':
                items = [rng.randint(5 if not shifted else 15, 95 if not shifted else 85) for _ in range(n)]
            elif family == 'weibull':
                items = [min(100, max(1, round(rng.weibullvariate(35, 1.5 if not shifted else 2.5)))) for _ in range(n)]
            elif family == 'complementary':
                k = 25 if not shifted else 40
                items = [rng.choice((k, 100-k))+rng.randint(-4, 4) for _ in range(n)]
            else:
                lo = [rng.randint(10, 35) for _ in range(n//2)]
                hi = [rng.randint(55, 85) for _ in range(n//2)]
                items = lo+hi if not shifted else hi+lo
            traces.append({'name':f'{family}_{rep}', 'family':family, 'items':items,
                           'l1_bound':math.ceil(sum(items)/CAP), 'capacity':CAP})
    return traces


def score(bins, traces):
    return [(n-t['l1_bound'])/t['l1_bound']*100 for n, t in zip(bins, traces)]


def conformance(traces):
    source = ROOT.parent / 'MetaMuse' / 'simulators' / 'bpp_core.py'
    raw = source.read_bytes()
    tree = ast.parse(raw.decode())
    selected = [x for x in tree.body if isinstance(x, ast.ClassDef) and x.name in ('Bin','BPPEval')]
    assert len(selected) == 2
    # These two full classes were read before execution. No package initializer,
    # pickle loader, generated code string, API or dependency installation runs.
    ns = {'List':list}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(source), 'exec'), ns)
    checks = []
    for pid in (0, 1, 31, 60, 124, 200, 312, 414, 500, 560, 600, 624):
        for t in traces:
            def policy(bins, item, g=GENOMES[pid]):
                return select(g, [b.remaining_space for b in bins], item)
            cfg = SimpleNamespace(instance={'items':t['items'], 'num_items':len(t['items']), 'capacity':CAP}, l1_bound=t['l1_bound'])
            ev = ns['BPPEval'](cfg, {'select_bin':policy, 'update_after_select':lambda *args: None})
            got = ev.simulate()*100
            expected = (pack(GENOMES[pid],t['items'])-t['l1_bound'])/t['l1_bound']*100
            assert abs(got-expected) < 1e-12
            checks.append({'policy':pid,'trace':t['name'],'score':got})
    return {'checks':len(checks), 'all_agree':True,'source_sha256':hashlib.sha256(raw).hexdigest()}


def landscape(train_bins, train_scores):
    classes = collections.defaultdict(list)
    for i, row in enumerate(train_bins):
        classes[tuple(row)].append(i)
    block = {p:k for k, group in enumerate(classes.values()) for p in group}
    kernel = [collections.Counter(block[mutation(p,l)] for l in range(8)) for p in range(len(GENOMES))]
    pairs = 0
    unequal = 0
    max_tv = 0
    witness = None
    for members in classes.values():
        for p,q in itertools.combinations(members,2):
            pairs += 1
            keys = kernel[p].keys() | kernel[q].keys()
            tv = sum(abs(kernel[p][k]-kernel[q][k]) for k in keys)/16
            unequal += tv > 0
            if tv > max_tv:
                max_tv = tv
                witness = {'p':p,'q':q,'p_genome':GENOMES[p],'q_genome':GENOMES[q],
                           'same_parent_bins':train_bins[p], 'tv':tv,
                           'p_child_mean_scores':[statistics.mean(train_scores[mutation(p,l)]) for l in range(8)],
                           'q_child_mean_scores':[statistics.mean(train_scores[mutation(q,l)]) for l in range(8)]}
    return {'programs':len(GENOMES),'performance_cells':len(classes),'non_singleton_cells':sum(len(v)>1 for v in classes.values()),
            'aliased_pairs':pairs,'different_uniform_transition_pairs':unequal,
            'fraction_different':unequal/pairs if pairs else None,'maximum_tv':max_tv,'witness':witness}


def distance(a,b):
    return sum((x-y)**2 for x,y in zip(a,b))/max(len(a),1)


def choose_archive(pool, records, method, rng):
    pool = sorted(set(pool))
    size = CFG['archive_size']
    quality = lambda p: (statistics.mean(records[p]['score']),p)
    best = min(pool,key=quality)
    if len(pool) <= size:
        return pool
    if method in ('fitness_flat',):
        return sorted(pool,key=quality)[:size]
    if method == 'reservoir':
        return sorted([best]+rng.sample([p for p in pool if p!=best],size-1))
    if method == 'offspring_quality':
        return sorted([best]+sorted([p for p in pool if p!=best],key=lambda p:(min(records[p]['probe_means']), quality(p)))[:size-1])
    def feature(p):
        rec=records[p]
        if method in ('performance','performance_flat'):
            return [x/100 for x in rec['score']]
        if method == 'syntax':
            return [x/2 for x in GENOMES[p]]
        if method == 'response':
            return [(x-y)/100 for row in rec['probes'] for x,y in zip(row,rec['score'])]
        if method == 'moments':
            vals=rec['probe_means']
            return [statistics.mean(vals)/100,statistics.pstdev(vals)/100]
        raise ValueError(method)
    chosen=[best]
    while len(chosen)<size:
        p=max((p for p in pool if p not in chosen),key=lambda p:(min(distance(feature(p),feature(q)) for q in chosen),-quality(p)[0],-p))
        chosen.append(p)
    return sorted(chosen)


def search(method, seed, scores):
    rng=random.Random(seed)
    initial=rng.sample(range(len(GENOMES)),CFG['initial_pool_size'])
    records={}
    history=[]
    seen=set()
    best=None
    calls=0
    def evaluate(p, role, parent=None, label=None):
        nonlocal calls,best
        calls+=1
        seen.add(p)
        value=statistics.mean(scores[p])
        if best is None or (value,p)<(statistics.mean(scores[best]),best): best=p
        history.append({'seed':seed,'method':method,'attempt':calls,'policy':p,'role':role,'parent':parent,'edit':label,'score':value,'best_policy':best,'best_score':statistics.mean(scores[best])})
        return list(scores[p])
    flat=method.endswith('_flat')
    def primary(p):
        val=evaluate(p,'primary')
        probes=[]
        if not flat:
            for l in CFG['probe_labels']:
                probes.append(evaluate(mutation(p,l),'probe',p,l))
        records[p]={'score':val,'probes':probes,'probe_means':[statistics.mean(x) for x in probes]}
    for p in initial: primary(p)
    archive=initial[:]
    while calls+(1 if flat else 3)<=CFG['evaluation_budget']:
        if method=='random_flat':
            p=rng.randrange(len(GENOMES))
        else:
            parent=rng.choice(archive)
            label=rng.randrange(8)
            p=mutation(parent,label)
        primary(p)
        if method != 'random_flat':
            archive=choose_archive(archive+[p],records,method,rng)
    return {'method':method,'seed':seed,'selected_policy':best,'train':statistics.mean(scores[best]),
            'attempts':calls,'unique_evaluated':len(seen),'primary_attempts':sum(x['role']=='primary' for x in history),
            'probe_attempts':sum(x['role']=='probe' for x in history),'valid_attempts':calls},history


def write_json(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2),encoding='utf-8')


def main():
    start=time.perf_counter()
    train=make_traces(CFG['train_seed'],False)
    test=make_traces(CFG['test_seed'],True)
    write_json('traces.json',{'train':train,'test':test})
    conformity=conformance(train[:2]+test[:2])
    train_bins=[]
    test_bins=[]
    for g in GENOMES:
        train_bins.append([pack(g,t['items']) for t in train])
        test_bins.append([pack(g,t['items']) for t in test])
    train_scores=[score(b,train) for b in train_bins]
    test_scores=[score(b,test) for b in test_bins]
    write_json('bank.json',{'genomes':GENOMES,'train_bins':train_bins,'test_bins':test_bins,
                            'train_scores':train_scores,'test_scores':test_scores})
    audit=landscape(train_bins,train_scores)
    write_json('landscape.json',audit)
    runs=[]
    history=[]
    for seed in range(CFG['search_seeds']):
        for method in CFG['methods']:
            run,h=search(method,seed,train_scores)
            run['test']=statistics.mean(test_scores[run['selected_policy']])
            runs.append(run)
            history.extend(h)
    for name,rows in [('runs.csv',runs),('search_history.csv',history)]:
        with (OUT/name).open('w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    summaries={}
    treatment=[r for r in runs if r['method']=='response']
    for method in CFG['methods']:
        group=[r for r in runs if r['method']==method]
        paired=[t['test']-r['test'] for t,r in zip(treatment,group)]
        summaries[method]={'mean_train':statistics.mean(r['train'] for r in group),
                           'mean_test':statistics.mean(r['test'] for r in group),
                           'test_sd':statistics.stdev(r['test'] for r in group),
                           'mean_unique_evaluated':statistics.mean(r['unique_evaluated'] for r in group),
                           'response_minus_baseline_test':statistics.mean(paired),
                           'response_wins_ties_losses':[sum(d< -1e-12 for d in paired),sum(abs(d)<=1e-12 for d in paired),sum(d>1e-12 for d in paired)]}
    summary={'config':CFG,'conformance':conformity,'landscape':audit,'methods':summaries,
             'actual_precomputation_candidate_trace_evaluations':len(GENOMES)*(len(train)+len(test)),
             'search_replay_charged_candidate_evaluations':sum(r['attempts'] for r in runs),
             'llm_calls':0,'llm_tokens':0,'api_cost_usd':0,
             'wall_seconds':time.perf_counter()-start,'python':platform.python_version(),
             'platform':platform.platform(),
             'scope':'Finite deterministic grammar and replay; no model-generated candidates; not a MetaMuse performance comparison'}
    write_json('summary.json',summary)
    hashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.rglob('*')) if p.is_file() and '__pycache__' not in str(p) and p.name!='hashes.json'}
    write_json('hashes.json',hashes)
    print(json.dumps({'landscape':audit,'methods':summaries,'wall_seconds':summary['wall_seconds']},indent=2))


if __name__=='__main__':main()
