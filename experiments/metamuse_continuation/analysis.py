"""Offline analysis only. No network API and no policy optimization.

The exact 32-credit integration averages subset/retention allocation on the
measured descendant matrix. It is not repeated sampling from the model.
"""
import argparse
import collections
import csv
import importlib.util
import itertools
import json
import math
from pathlib import Path
import statistics
import time

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('cont',ROOT/'continuation.py')
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)


def csvfile(path,rows):
    with (ROOT/path).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def exact_training():
    if (ROOT/'exact_training_selection.json').exists():raise SystemExit('Exact training integration already frozen')
    logical=C.logical_records();attempts={r['attempt_id']:r for r in C.attempt_records()}
    if len(logical)!=64 or any(len(r['attempt_ids'])!=1 for r in logical):
        C.save('exact_training_selection.json',{'available':False,'reason':'Requires complete matrix without retry clusters; ordinary replay remains valid.'});return
    ps,pr=C.parents(),C.probes()
    quality={p:(v['evaluation']['mean'],p) for p,v in ps.items()}
    sources={p:('prior',v['source']) for p,v in ps.items()}
    for r in C.legacy_records():
        if r['role']=='probe' and r['evaluation']['valid']:
            quality[r['id']]=(r['evaluation']['mean'],r['id']);sources[r['id']]=('prior','calls/'+r['id']+'/program.py')
    for r in logical:
        if r['evaluation']['valid']:
            quality[r['logical_id']]=(r['evaluation']['mean'],r['logical_id'])
            sources[r['logical_id']]=('continuation','calls/'+r['final_attempt_id']+'/program.py')
    minima=lambda ids:min(ids,key=lambda p:quality[p])
    methods={}
    for method in C.METHODS:
        probe_events=[]
        if method in C.PROBE_METHODS:
            probe_events=[r for p in pr for r in pr[p] if method!='response_local' or r['edit']=='local']
        base=minima(list(ps)+[r['id'] for r in probe_events if r['evaluation']['valid']])
        per_parent=(32-len(probe_events))//4;per_label=per_parent//2
        assert 4*per_parent+len(probe_events)==32
        choices=range(70) if method=='random' else range(16) if method=='neutral' else range(1)
        final=collections.defaultdict(float);expected_cost=0;expected_eval=0
        for choice in choices:
            chosen=C.select(method,ps,pr,choice)
            dist={base:1.}
            run_cost=sum(C.nominal(r['usage']) for r in probe_events)
            run_eval=sum(p['evaluation']['seconds'] for p in ps.values())+sum(r['evaluation'].get('seconds',0) for r in probe_events)
            for p in chosen:
                local=[r for r in logical if r['parent']==p and r['edit']=='local']
                alternative=[r for r in logical if r['parent']==p and r['edit']=='alternative']
                assert len(local)==len(alternative)==4
                subsets=list(itertools.product(itertools.combinations(local,per_label),itertools.combinations(alternative,per_label)))
                pd=collections.defaultdict(float)
                for a,b in subsets:
                    child=minima([base]+[r['logical_id'] for r in a+b if r['evaluation']['valid']])
                    pd[child]+=1/len(subsets)
                combined=collections.defaultdict(float)
                for a,pa in dist.items():
                    for b,pb in pd.items():combined[minima([a,b])]+=pa*pb
                dist=combined
                run_cost+=per_label/4*sum(attempts[r['final_attempt_id']]['nominal_cny'] for r in local+alternative)
                run_eval+=per_label/4*sum(r['evaluation'].get('seconds',0) for r in local+alternative)
            for cid,prob in dist.items():final[cid]+=prob/len(choices)
            expected_cost+=run_cost/len(choices);expected_eval+=run_eval/len(choices)
        assert abs(sum(final.values())-1)<1e-10
        methods[method]={'output_probabilities':dict(final),'expected_train_mean':sum(quality[cid][0]*p for cid,p in final.items()),
            'expected_nominal_cny':expected_cost,'expected_evaluation_seconds':expected_eval,
            'attempts':32,'probe_attempts':len(probe_events),'future_samples_per_retained_parent':per_parent}
    C.save('exact_training_selection.json',{'utc':C.stamp(),'available':True,'methods':methods,
        'support_sources':{cid:list(sources[cid]) for cid in set().union(*(set(x['output_probabilities']) for x in methods.values()))},
        'heldout_accessed':False,'definition':'Exact expectation over finite-bank label-balanced subsets and random/neutral parent-set choices; not independent model searches.'})
    print(json.dumps({'exact_training_frozen':True,'supported_candidates':len(set().union(*(set(x['output_probabilities']) for x in methods.values())))}))


def evaluate_test():
    if (ROOT/'heldout_results.json').exists():raise SystemExit('Heldout results already exist')
    cfg=C.read('config.json');freeze=C.read('selection_freeze.json')
    assert C.sha((ROOT/'replay_training.json').read_bytes())==freeze['replay_sha256']
    assert C.sha((ROOT/'workloads/new_heldout.json').read_bytes())==cfg['new_test_sha256']
    replay=C.read('replay_training.json');ps=C.parents()
    sources={p:('prior',v['source']) for p,v in ps.items()}
    # Score the full eligible corpus after freezing selection, enabling complete
    # raw evaluation and exact conditional integration without test-based search.
    for e in replay['event_catalog'].values():
        if e['evaluation']['valid']:sources[e['candidate_id']]=(e['source_root'],e['source_path'])
    sources['old_champion_reference']=('prior','calls/future_p06_02/program.py')
    exact=C.read('exact_training_selection.json')
    if exact['available']:assert set(exact['support_sources'])<=set(sources)
    traces=C.read('workloads/new_heldout.json');cache={};evaluations={}
    started=time.perf_counter()
    for cid,(where,path) in sorted(sources.items()):
        source=((C.OLD if where=='prior' else ROOT)/path).read_text(encoding='utf-8');h=C.sha(source)
        if h not in cache:
            pertrace=[]
            for t in traces:
                ev=C.M.evaluate(source,[t])
                pertrace.append({'name':t['name'],'bank':t['bank'],'family':t['family'],'valid':ev['valid'],
                    'score':ev['mean'] if ev['valid'] else 100*(192-t['l1_bound'])/t['l1_bound'],
                    'penalized_test_failure':not ev['valid'],'reason':ev.get('reason'),
                    'bins':ev['bins'][0] if ev['valid'] else None,'seconds':ev['seconds']})
            cache[h]={'source_sha256':h,'valid':all(e['valid'] for e in pertrace),
                'mean':statistics.mean(e['score'] for e in pertrace),
                'bank_means':[statistics.mean(e['score'] for e in pertrace if e['bank']==b) for b in range(8)],
                'per_trace':pertrace}
        evaluations[cid]=cache[h]
        if len(evaluations)%8==0:print(json.dumps({'new_test_candidates_scored':len(evaluations),'unique_sources':len(cache)}),flush=True)
    C.save('heldout_results.json',{'utc':C.stamp(),'selection_sha256':freeze['replay_sha256'],
        'exact_selection_sha256':C.sha((ROOT/'exact_training_selection.json').read_bytes()),
        'test_sha256':cfg['new_test_sha256'],'evaluations':evaluations,
        'fresh_test_traces':96,'workload_banks':8,'independent_model_search_banks':1,
        'evaluation_wall_seconds':time.perf_counter()-started,'unique_sources':len(cache)})
    print(json.dumps({'new_test_done':True,'candidates':len(evaluations),'all_valid':all(e['valid'] for e in evaluations.values())}))


def summarize():
    data=C.read('replay_training.json');test=C.read('heldout_results.json')['evaluations'];cfg=C.read('config.json')
    allrows=[]
    for r in data['rows']:
        ev=test[r['best_id']]
        allrows.append({**r,'new_test_mean':ev['mean'],'new_test_valid':ev['valid'],'bank_means':ev['bank_means']})
    C.save('comparison_rows.json',{'rows':allrows,'allocation_draws_are_not_model_trials':True})
    summary=[]
    for view,budget in [('credits',8),('credits',16),('credits',24),('credits',32),('priced',32)]:
        for method in C.METHODS:
            rows=[r for r in allrows if r['method']==method and r['view']==view and r['budget_attempts']==budget]
            summary.append({'method':method,'view':view,'budget_attempts':budget,
                'mean_train':statistics.mean(r['train_mean'] for r in rows),
                'mean_new_test':statistics.mean(r['new_test_mean'] for r in rows),
                'mean_attempts':statistics.mean(r['attempts'] for r in rows),
                'mean_nominal_cny':statistics.mean(r['nominal_cny'] for r in rows),
                'mean_conservative_cny':statistics.mean(r['conservative_cny'] for r in rows),
                'mean_evaluation_seconds':statistics.mean(r['evaluation_seconds_including_common'] for r in rows),
                'mean_request_wall_seconds':statistics.mean(r['reconstructed_request_wall_seconds'] for r in rows),
                'pool_censored_fraction':statistics.mean(r['pool_censored'] for r in rows),
                'invalid_chosen_fraction':statistics.mean(not r['new_test_valid'] for r in rows),
                'mean_unused_money':statistics.mean(cfg['priced_budget_cny']-r['nominal_cny'] for r in rows) if view=='priced' else None})
    csvfile('baseline_comparisons.csv',summary)
    exact=C.read('exact_training_selection.json');exact_results={}
    if exact['available']:
        for method,x in exact['methods'].items():
            probs=x['output_probabilities']
            exact_results[method]={**x,'expected_new_test':sum(test[c]['mean']*p for c,p in probs.items()),
                'expected_bank_means':[sum(test[c]['bank_means'][b]*p for c,p in probs.items()) for b in range(8)],
                'test_invalid_probability':sum(p for c,p in probs.items() if not test[c]['valid'])}
    C.save('exact_conditional_comparison.json',{'available':exact['available'],'methods':exact_results,
        'definition':'Exact finite-bank allocation expectation, not additional LLM experiments.'})
    if exact['available']:
        csvfile('baseline_comparisons_exact.csv',[{'method':m,'attempt_budget':32,
            'expected_train_mean':x['expected_train_mean'],'expected_new_test':x['expected_new_test'],
            'expected_nominal_cny':x['expected_nominal_cny'],'probe_attempts':x['probe_attempts'],
            'expected_evaluation_seconds':x['expected_evaluation_seconds'],
            'fresh_samples_per_parent':x['future_samples_per_retained_parent'],
            'invalid_test_probability':x['test_invalid_probability']} for m,x in exact_results.items()])
    paired=[]
    for view in ['credits','priced']:
        bymethod={m:[r for r in allrows if r['method']==m and r['view']==view and r['budget_attempts']==32] for m in C.METHODS}
        for treatment in ['response_current','response_masked','response_complete','response_local']:
            for baseline in ['performance','random','neutral','performance_cells_short','structural','offspring_quality','probe_control','validity_only']:
                a,b=bymethod[treatment],bymethod[baseline]
                if view=='credits' and exact['available']:
                    diffs=[exact_results[treatment]['expected_bank_means'][k]-exact_results[baseline]['expected_bank_means'][k] for k in range(8)]
                else:
                    diffs=[statistics.mean(r['bank_means'][k] for r in a)-statistics.mean(r['bank_means'][k] for r in b) for k in range(8)]
                # Numerical equality must not become a spurious nonzero interval.
                diffs=[0. if abs(x)<1e-12 else x for x in diffs]
                mean=statistics.mean(diffs);half=2.364624251*statistics.stdev(diffs)/math.sqrt(8)
                cost_difference=(exact_results[treatment]['expected_nominal_cny']-exact_results[baseline]['expected_nominal_cny']) if view=='credits' and exact['available'] else statistics.mean(r['nominal_cny'] for r in a)-statistics.mean(r['nominal_cny'] for r in b)
                paired.append({'view':view,'treatment':treatment,'baseline':baseline,'difference_test_lower_is_better':mean,
                    'workload_bank_ci95_low':mean-half,'workload_bank_ci95_high':mean+half,
                    'mean_cost_difference_cny':cost_difference,
                    'integration':'exact finite-bank' if view=='credits' and exact['available'] else '560 conditional allocations',
                    'warning':'CI covers eight fresh workload-bank draws conditional on one measured descendant matrix; no independent-model replication claim.'})
    csvfile('paired_workload_comparisons.csv',paired)
    ps=C.parents();pr=C.probes();ats=C.attempt_records();logical=C.logical_records()
    best_initial=min(p['evaluation']['mean'] for p in ps.values())
    perparent=[]
    for p in sorted(ps):
        group=[r for r in logical if r['parent']==p];valid=[r for r in group if r['evaluation']['valid']]
        perparent.append({'parent':p,'future_attempts':sum(len(r['attempt_ids']) for r in group),'future_outputs':len(group),
            'future_valid':len(valid),'future_parent_improvements':sum(r['evaluation']['mean']<ps[p]['evaluation']['mean']-1e-10 for r in valid),
            'future_global_improvements':sum(r['evaluation']['mean']<best_initial-1e-10 for r in valid),
            'future_best_train':min([r['evaluation']['mean'] for r in valid]+[ps[p]['evaluation']['mean']]),
            'old_probe_valid':sum(r['evaluation']['valid'] for r in pr[p])})
    C.save('discovery_diagnostic.json',{'per_parent':perparent,
        'fresh_global_improving_candidates':[r['logical_id'] for r in logical if r['evaluation']['valid'] and r['evaluation']['mean']<best_initial-1e-10],
        'initial_seed_new_test':{p:test[p]['mean'] for p in ps},'old_champion_new_test':test['old_champion_reference']['mean'],
        'old_champion_not_used_in_selection':True,'new_valid_fraction':sum(r['evaluation']['valid'] for r in logical)/len(logical)})
    candidate_rows=[]
    for r in logical:
        ev=r['evaluation'];te=test.get(r['logical_id'],{})
        candidate_rows.append({'logical_id':r['logical_id'],'parent':r['parent'],'edit':r['edit'],
            'attempt_ids':','.join(r['attempt_ids']),'train_valid':ev['valid'],'train_mean':ev.get('mean'),
            'test_valid':te.get('valid'),'new_test_mean':te.get('mean'),'failure':ev.get('reason','')})
    csvfile('candidate_evaluations.csv',candidate_rows)
    C.save('analysis_summary.json',{'primary_summaries':[r for r in summary if r['budget_attempts']==32],
        'new_actual_ledger':C.read('ledger.json'),'all_primary_pool_uncensored':not any(r['pool_censored_fraction'] for r in summary if r['budget_attempts']==32),
        'model_search_matrices':1,'fresh_workload_banks':8,'allocation_count':560,
        'allocation_count_is_not_sample_size':True,'exact_allocation_integration_available':exact['available']})
    print(json.dumps({'primary':[r for r in summary if r['budget_attempts']==32],
        'discovery':C.read('discovery_diagnostic.json')},indent=2),flush=True)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['exact','heldout','summarize']);a=ap.parse_args()
    if a.command=='exact':exact_training()
    elif a.command=='heldout':evaluate_test()
    else:summarize()
