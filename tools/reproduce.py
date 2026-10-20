"""Offline replay from recorded artifacts; no acquisition, tuning or new search bank.

Python 3.10+, standard library only. All writes go to an ignored output folder.
Network connections are disabled for the entire process before project imports.
"""
import argparse
import contextlib
import csv
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import runpy
import shutil
import socket
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
def deny_network(*args,**kwargs):raise RuntimeError('Offline reproduction forbids network connections')
socket.socket.connect=deny_network
socket.create_connection=deny_network
def load(p):
    if p.exists():return json.loads(p.read_text(encoding='utf-8'))
    return json.loads(gzip.decompress(Path(str(p)+'.gz').read_bytes()))
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def write(p,x):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def near(a,b):return abs(float(a)-float(b))<=1e-10

def verify():
    manifest=load(ROOT/'ARTIFACT_MANIFEST.json')
    assert manifest['schema']==1
    bad=[p for p,h in manifest['files'].items() if not (ROOT/p).is_file() or hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
    assert not bad, bad
    actual={p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.relative_to(ROOT).parts and '.reproduced' not in p.relative_to(ROOT).parts and '__pycache__' not in p.relative_to(ROOT).parts and p.name!='ARTIFACT_MANIFEST.json'}
    assert actual==set(manifest['files']), ('unmanifested/missing files',sorted(actual^set(manifest['files'])))
    print(json.dumps({'manifest_files_verified':len(manifest['files']),'network_disabled':True}))

def cpu(out):
    base=ROOT/'experiments/metamuse_pilot'
    p=module('pilot',base/'pilot.py')
    bank=load(base/'results/bank.json')
    land=p.landscape(bank['train_bins'],bank['train_scores'])
    expected=load(base/'results/landscape.json')
    for k in ('programs','aliased_pairs','different_uniform_transition_pairs','performance_cells'):
        assert land[k]==expected[k]
    result={}
    for sub,fn,cfg in [('results',p.search,p.CFG),
        ('selective_results_corrected',module('selective',base/'selective_pilot.py').run,load(base/'selective_config.json'))]:
        b=load(base/sub/'bank.json');rows=[]
        for seed in range(cfg['search_seeds']):
            for method in cfg['methods']:
                row,_=fn(method,seed,b['train_scores'])
                row['test']=statistics.mean(b['test_scores'][row['selected_policy']]);rows.append(row)
        frozen=list(csv.DictReader((base/sub/'runs.csv').open(encoding='utf-8')))
        assert len(rows)==len(frozen)
        for x,y in zip(rows,frozen):
            assert x['method']==y['method'] and x['seed']==int(y['seed'])
            for k in ('train','test','selected_policy','attempts'):assert near(x[k],y[k]),(sub,k,x,y)
        means={m:{'train':statistics.mean(r['train'] for r in rows if r['method']==m),
                  'test':statistics.mean(r['test'] for r in rows if r['method']==m)} for m in cfg['methods']}
        result[sub]={'reproduced_rows':len(rows),'means':means}
    write(out/'cpu_replay.json',{'landscape':land,'comparisons':result,'new_candidate_evaluations':0})
    print(json.dumps({'cpu_cached_landscape_pairs':land['different_uniform_transition_pairs'],'comparison_rows_verified':sum(x['reproduced_rows'] for x in result.values()),'new_candidate_evaluations':0}))

def initial():
    with contextlib.redirect_stdout(io.StringIO()) as capture:
        runpy.run_path(str(ROOT/'experiments/metamuse_llm_pilot/reproduce_offline.py'),run_name='__main__')
    print(capture.getvalue().strip())

def continuation(out):
    base=ROOT/'experiments/metamuse_continuation'
    # Historical freeze writer hashes a physical config next to its outputs.
    # Copy only this small immutable input, without changing published evidence.
    shutil.copyfile(base/'config.json',out/'config.json')
    a=module('continuation_analysis',base/'analysis.py');c=a.C
    source_read=lambda name:load(base/name)
    c.read=lambda name:load(out/name) if (out/name).exists() else source_read(name)
    c.attempt_records=lambda:[load(p) for p in sorted((base/'calls').glob('*/result.json'))]
    c.logical_records=lambda:[load(p) for p in sorted((base/'logical').glob('*.json'))]
    c.save=lambda name,obj:write(out/name,obj)
    c.ROOT=out;a.ROOT=out
    with contextlib.redirect_stdout(io.StringIO()):
        c.replay();a.exact_training();a.summarize()
    actual=list(csv.DictReader((out/'baseline_comparisons_exact.csv').open(encoding='utf-8')))
    frozen=list(csv.DictReader((base/'baseline_comparisons_exact.csv').open(encoding='utf-8')))
    assert len(actual)==len(frozen)==12
    for x,y in zip(actual,frozen):
        assert x['method']==y['method']
        for k in y:
            if k!='method':assert near(x[k],y[k]),(x['method'],k,x[k],y[k])
    # Host selector computation time is newly measured; recorded API/evaluation
    # times and scientific budget decisions must retain their historical meaning.
    primary=list(csv.DictReader((out/'baseline_comparisons.csv').open(encoding='utf-8')))
    saved=list(csv.DictReader((base/'baseline_comparisons.csv').open(encoding='utf-8')))
    assert len(primary)==len(saved)==60
    keys=('mean_train','mean_new_test','mean_attempts','mean_nominal_cny','mean_conservative_cny','pool_censored_fraction','invalid_chosen_fraction')
    for x,y in zip(primary,saved):
        assert (x['method'],x['view'],x['budget_attempts'])==(y['method'],y['view'],y['budget_attempts'])
        for k in keys:assert near(x[k],y[k]),(x['method'],x['view'],k,x[k],y[k])
    print(json.dumps({'exact_32_credit_methods_verified':12,'all_horizon_and_priced_rows_verified':60,
        'allocation_replays_not_independent_model_trials':True,'paid_calls':0,'fresh_program_evaluations':0}))

def evaluator():
    base=ROOT/'experiments/metamuse_llm_pilot';m=module('scalar_evaluator',base/'llm_pilot.py')
    parents=load(base/'parents.json');traces=load(base/'workloads/train.json');count=0
    for p in parents:
        ev=m.evaluate((base/p['source']).read_text(encoding='utf-8'),traces)
        assert ev['valid'] and ev['bins']==p['evaluation']['bins'];count+=len(traces)
    print(json.dumps({'existing_seed_trace_evaluations_verified':count,'generated_programs_executed_by_python':0,'paid_calls':0}))

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command',choices=['verify','cpu','initial','continuation','evaluator','all'])
    ap.add_argument('--out',default='.reproduced')
    args=ap.parse_args();out=(ROOT/args.out).resolve()
    if args.command in ('cpu','continuation','all'):
        # Never write into published experiment, source or note directories.
        assert out!=ROOT and ROOT in out.parents and out.relative_to(ROOT).parts[0]=='.reproduced', 'Output must be below .reproduced/'
        if out.exists() and any(out.iterdir()):raise SystemExit('Output already populated; use a new --out .reproduced/<name>')
        out.mkdir(parents=True,exist_ok=True)
    if args.command in ('verify','all'):verify()
    if args.command in ('cpu','all'):cpu(out/'cpu')
    if args.command in ('initial','all'):initial()
    if args.command in ('continuation','all'):
        (out/'continuation').mkdir(parents=True,exist_ok=True);continuation(out/'continuation')
    if args.command in ('evaluator','all'):evaluator()
if __name__=='__main__':main()
