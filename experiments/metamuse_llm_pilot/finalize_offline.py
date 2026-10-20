"""Export complete accounting, balanced-bank curves and interrupted-run data.

This file contains no model client and cannot make network requests. Policy
choices come only from the replay frozen before held-out evaluation.
"""
import collections
import csv
import hashlib
import json
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parent
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def save(p,x):(ROOT/p).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def avg(x):return statistics.mean(x) if x else None
def write_csv(name,rows):
    with (ROOT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def main():
    rs=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'calls').glob('*/result.json'))]
    byid={r['id']:r for r in rs}
    nominal={}
    nominal_rows=[]
    for r in rs:
        usage=r['usage']
        if usage:
            inp,out=usage['prompt_tokens'],usage['completion_tokens']
            cached=usage.get('prompt_tokens_details',{}).get('cached_tokens',0)
            ip,op,cp=(2,8,.4) if inp<32000 and out<200 else (3,14,.6) if inp<32000 else (4,16,.8)
            price=((inp-cached)*ip+cached*cp+out*op)/1e6
        else:
            inp,out,cached,ip,op,cp=None,None,None,4,16,None
            price=r['cost_cny']
        nominal[r['id']]=price
        nominal_rows.append({'id':r['id'],'prompt_tokens':inp,'completion_tokens':out,'cached_tokens':cached,
            'input_price_cny_per_million':ip,'output_price_cny_per_million':op,
            'estimated_cny_or_failure_reserve':price,'usage_known':usage is not None})
    save('nominal_price_accounting.json',{'source':'sources/pricing.md','total_cny_including_unknown_call_reserve':sum(nominal.values()),
        'warning':'Official tier-aware token estimate, not account invoice; unknown failed call uses full higher-tier reserve.', 'calls':nominal_rows})
    parents={p['id']:p for p in read('parents.json')}
    frozen=read('training_replay.json');comparison=read('comparison.json')
    test=read('heldout_evaluations.json')['evaluations']
    initial_best=min(parents,key=lambda p:(parents[p]['evaluation']['mean'],p))
    best_initial_train=parents[initial_best]['evaluation']['mean']
    balanced_ids={r['id'] for r in read('schedule.json')[:48]}
    valid=[r for r in rs if r['evaluation']['valid']]
    all_useful=[r for r in valid if r['evaluation']['mean']<parents[r['parent']]['evaluation']['mean']-1e-10]
    actual={'actual_attempts':len(rs),'successful_api_responses':sum(r['http_success'] for r in rs),
        'executable_responses':len(valid),'valid_rate_per_attempt':len(valid)/len(rs),
        'valid_rate_per_completed_response':len(valid)/sum(r['http_success'] for r in rs),
        'network_failures':sum(not r['http_success'] for r in rs),
        'execution_or_parse_failures':sum(r['http_success'] and not r['evaluation']['valid'] for r in rs),
        'retries':0,'balanced_comparison_bank_attempts':48,
        'interrupted_stage_attempts':len(rs)-48,
        'input_tokens_known':sum((r['usage'] or {}).get('prompt_tokens',0) for r in rs),
        'output_tokens_known':sum((r['usage'] or {}).get('completion_tokens',0) for r in rs),
        'cost_cny_upper':sum(r['cost_cny'] for r in rs),
        'tier_aware_list_price_cny_plus_unknown_reserve':sum(nominal.values()),
        'cost_cny_list_estimate_plus_unknown_reserve':sum(((r['usage']['prompt_tokens']*3+r['usage']['completion_tokens']*14)/1e6 if r['usage'] else r['cost_cny']) for r in rs),
        'unknown_usage_reserved_calls':sum(r['usage'] is None for r in rs),
        'request_wall_seconds_sum':sum(r['wall_seconds'] for r in rs),
        'train_execution_seconds_sum':sum(r['evaluation'].get('seconds',0) for r in rs),
        'initial_common_evaluations':8,'initial_common_eval_seconds':sum(p['evaluation']['seconds'] for p in parents.values()),
        'distinct_valid_source_hashes':len({r['program_sha256'] for r in valid}),
        'distinct_valid_training_action_signatures':len({tuple(r['evaluation']['action_hashes']) for r in valid}),
        'distinct_valid_training_score_vectors':len({tuple(r['evaluation']['bins']) for r in valid}),
        'parent_relative_useful_children':len(all_useful),
        'distinct_parent_relative_useful_source_hashes':len({r['program_sha256'] for r in all_useful}),
        'distinct_parent_relative_useful_action_signatures':len({tuple(r['evaluation']['action_hashes']) for r in all_useful}),
        'strict_global_training_improvements':[r['id'] for r in valid if r['evaluation']['mean']<best_initial_train-1e-10],
        'model_aliases':dict(collections.Counter(r.get('returned_model','unknown') for r in rs if r['http_success'])),
        'failure_cost_is_reserved_not_observed_billing':True,
        'usd_upper_bound_uses_deliberate_1_cny_to_1_usd':True}
    save('accounting_final.json',actual)
    candidate_rows=[]
    for cid,p in parents.items():
        candidate_rows.append({'id':cid,'role':'human_seed','parent':'','in_balanced_bank':True,
            'api_success':None,'train_valid':True,'train_mean':p['evaluation']['mean'],
            'heldout_valid':test[cid]['valid'],'heldout_mean':test[cid].get('mean'),
            'parent_relative_train_improvement':None,'generation_cost_cny':0,'input_tokens':0,'output_tokens':0,
            'request_wall_seconds':0,'train_eval_seconds':p['evaluation']['seconds'],
            'canonical_source_sha256':p['sha256'],'failure':''})
    for r in rs:
        ev=r['evaluation'];te=test.get(r['id'],{})
        candidate_rows.append({'id':r['id'],'role':r['role'],'parent':r['parent'],
            'in_balanced_bank':r['id'] in balanced_ids,'api_success':r['http_success'],
            'train_valid':ev['valid'],'train_mean':ev.get('mean'),'heldout_valid':te.get('valid'),
            'heldout_mean':te.get('mean'),
            'parent_relative_train_improvement':parents[r['parent']]['evaluation']['mean']-ev['mean'] if ev['valid'] else None,
            'generation_cost_cny':r['cost_cny'],'input_tokens':(r['usage'] or {}).get('prompt_tokens'),
            'output_tokens':(r['usage'] or {}).get('completion_tokens'),
            'request_wall_seconds':r['wall_seconds'],'train_eval_seconds':ev.get('seconds',0),
            'canonical_source_sha256':r.get('program_sha256'),'failure':ev.get('reason','')})
    write_csv('candidate_evaluations.csv',candidate_rows)
    summary=[]
    for entry in comparison['summary']:
        sub=[r for r in comparison['rows'] if r['view']==entry['view'] and r['method']==entry['method']]
        summary.append({**entry,'mean_replayed_request_wall_seconds':avg([sum(byid[i]['wall_seconds'] for i in r['events']) for r in sub]),
            'mean_tier_aware_list_cost_cny':avg([sum(nominal[i] for i in r['events']) for r in sub]),
            'warning':'balanced 48-call bank; pool censoring prevents full 48-per-policy endpoint'})
    write_csv('baseline_comparisons.csv',summary)
    # Curves for every declared budget interval, rather than selecting a favorable point.
    curves=[]
    base=frozen['rows']
    for r in base:
        if r['view']!='attempts':continue
        for view,limits in [('attempts',range(0,49,4)),('priced',[i/1000 for i in range(0,101,10)])]:
            for limit in limits:
                best=initial_best;bestval=best_initial_train;cost=0;events=[]
                for cid in r['events']:
                    call=byid[cid]
                    if len(events)>=48 or view=='attempts' and len(events)>=limit or view=='priced' and cost+call['cost_cny']>limit+1e-12:break
                    events.append(cid);cost+=call['cost_cny']
                    if call['evaluation']['valid'] and (call['evaluation']['mean'],cid)<(bestval,best):best,bestval=cid,call['evaluation']['mean']
                exhausted=len(events)==len(r['events']) and ((len(events)<limit) if view=='attempts' else cost<limit-1e-12)
                curves.append({'seed':r['seed'],'method':r['method'],'budget_view':view,'budget':limit,
                    'attempts_used':len(events),'cost_cny_used':cost,'source_pool_censored':exhausted,
                    'best_id':best,'train_mean':bestval,'heldout_mean':test[best]['mean'],
                    'eval_seconds':sum(byid[i]['evaluation'].get('seconds',0) for i in events)})
    write_csv('cost_curves.csv',curves)
    early=[]
    for method in read('config.json')['methods']:
        sub=[r for r in curves if r['budget_view']=='attempts' and r['budget']==16 and r['method']==method]
        early.append({'method':method,'attempt_credits':16,'mean_heldout':avg([r['heldout_mean'] for r in sub]),
            'mean_cost_cny':avg([r['cost_cny_used'] for r in sub]),'censored':any(r['source_pool_censored'] for r in sub)})
    save('fully_available_16_credit_comparison.json',{'role':'prespecified cost-curve diagnostic; does not replace planned 48-credit endpoint','rows':early})
    # Same-performing representation-pair prediction diagnostic from balanced data only.
    rows=read('snapshots/at_48/scientific_summary.json')['per_parent']
    paired=[]
    for a,b in zip(rows[::2],rows[1::2]):
        x=a['probe']['useful_rate_all_attempts']-b['probe']['useful_rate_all_attempts']
        y=a['future']['useful_rate_all_attempts']-b['future']['useful_rate_all_attempts']
        paired.append({'a':a['parent'],'b':b['parent'],'probe_useful_rate_difference':x,
            'independent_future_useful_rate_difference':y,
            'direction_agrees_when_both_nonzero':x*y>0 if abs(x)>1e-12 and abs(y)>1e-12 else None})
    save('prediction_diagnostic.json',{'balanced_future_samples_per_parent':4,'probe_samples_per_parent':2,
        'equivalent_pairs':paired,'warning':'Only four pairs; exploratory description, no kernel or significance claim'})
    best=min(valid,key=lambda r:(r['evaluation']['mean'],r['id']))
    pertrace=[]
    traces=read('workloads/heldout.json')
    for t,a,b in zip(traces,test[initial_best]['scores'],test[best['id']]['scores']):
        pertrace.append({'trace':t['name'],'family':t['family'],'initial_best':a,'training_selected_child':b,'difference_child_minus_initial':b-a})
    save('candidate_improvement.json',{'id':best['id'],'chosen_using':'minimum training mean over every available executable response, ID tie-break',
        'parent':best['parent'],'initial_train_mean':best_initial_train,'child_train_mean':best['evaluation']['mean'],
        'initial_heldout_mean':test[initial_best]['mean'],'child_heldout_mean':test[best['id']]['mean'],
        'heldout_absolute_improvement_pp':test[initial_best]['mean']-test[best['id']]['mean'],
        'heldout_relative_reduction_in_excess_metric':1-test[best['id']]['mean']/test[initial_best]['mean'],
        'per_trace':pertrace,'novelty':'No novelty or state-of-the-art claim for this heuristic'})
    save('FINAL_DECISION.json',{'classification':'INCONCLUSIVE',
        'candidate_result':'One genuine LLM edit improves both frozen training and held-out scores over the initial best seed.',
        'method_result':'No demonstrated cost-matched advantage over cheap controls. Balanced bank is incomplete for the planned endpoint; early matched-credit view favors cheap random/neutral allocation.',
        'research_go':'NO-GO for claiming a new selection method or launching another paid round automatically.',
        'why_stopped':'Attempt 60 connection failure; zero retry policy honored. Later stage uneven; no test-driven resumption.',
        'next_authorized_actions':'Only artifact verification and reporting; no email or additional paid experiment.'})
    print(json.dumps({'accounting':actual,'early_equal_credit':early,'prediction_pairs':paired},indent=2))


if __name__=='__main__':main()
