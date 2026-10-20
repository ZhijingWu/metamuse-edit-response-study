"""Read-only scientific summaries and pre-test futility gate. No network code."""
import collections
import hashlib
import itertools
import json
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parent


def load(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def save(name,x):(ROOT/name).write_text(json.dumps(x,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def avg(x):return statistics.mean(x) if x else None


def correlation(x,y):
    if len(x)<2 or statistics.pstdev(x)==0 or statistics.pstdev(y)==0:return None
    return statistics.correlation(x,y)


def main():
    ps={p['id']:p for p in load('parents.json')}
    rs=[json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'calls').glob('*/result.json'))]
    replay=load('training_replay.json') if (ROOT/'training_replay.json').exists() else None
    per_parent=[]
    global_best=min(p['evaluation']['mean'] for p in ps.values())
    for pid,p in ps.items():
        row={'parent':pid,'parent_train_mean':p['evaluation']['mean']}
        for role in ['probe','future']:
            sub=[r for r in rs if r['parent']==pid and r['role']==role]
            valid=[r for r in sub if r['evaluation']['valid']]
            useful=[r for r in valid if r['evaluation']['mean']<p['evaluation']['mean']-1e-10]
            novel=[r for r in valid if r['evaluation']['mean']<global_best-1e-10]
            row[role]={'attempts':len(sub),'valid':len(valid),'useful':len(useful),
                'useful_rate_all_attempts':len(useful)/len(sub) if sub else None,
                'distinct_useful_sources':len({r['program_sha256'] for r in useful}),
                'distinct_useful_behaviors':len({tuple(r['evaluation']['action_hashes']) for r in useful}),
                'strictly_better_than_initial_global_best':len(novel),
                'mean_valid_child_cost':avg([r['evaluation']['mean'] for r in valid]),
                'mean_improvement_including_invalid_penalty':avg([p['evaluation']['mean']-r['evaluation'].get('mean',p['evaluation']['mean']+100) for r in sub]),
                'cost_cny':sum(r['cost_cny'] for r in sub)}
        per_parent.append(row)
    pairs=[]
    for a,b in zip(list(ps)[::2],list(ps)[1::2]):
        byid={r['parent']:r for r in per_parent}
        row={'a':a,'b':b,'same_parent_training_bins':ps[a]['evaluation']['bins']==ps[b]['evaluation']['bins'],
             'same_parent_training_actions':ps[a]['evaluation']['action_hashes']==ps[b]['evaluation']['action_hashes']}
        for role in ['probe','future']:
            x,y=byid[a][role],byid[b][role]
            row[role+'_useful_rate_difference_a_minus_b']=None if x['useful_rate_all_attempts'] is None or y['useful_rate_all_attempts'] is None else x['useful_rate_all_attempts']-y['useful_rate_all_attempts']
        for edit in ['local','alternative']:
            sub=[r for r in rs if r['parent'] in [a,b] and r['role']=='probe' and r['edit']==edit]
            if len(sub)==2:
                row[edit+'_probe_different_sampled_outcome']=sub[0]['evaluation'].get('bins')!=sub[1]['evaluation'].get('bins')
        pairs.append(row)
    valid=[r for r in rs if r['evaluation']['valid']]
    details={'real_attempts':len(rs),'valid':len(valid),'invalid':len(rs)-len(valid),
        'api_successes':sum(r['http_success'] for r in rs),'automatic_retries':0,
        'failures':[{'id':r['id'],'reason':r['evaluation'].get('reason')} for r in rs if not r['evaluation']['valid']],
        'distinct_valid_source_hashes':len({r['program_sha256'] for r in valid}),
        'distinct_valid_training_action_signatures':len({tuple(r['evaluation']['action_hashes']) for r in valid}),
        'distinct_valid_training_score_vectors':len({tuple(r['evaluation']['bins']) for r in valid}),
        'strict_global_improvements':[r['id'] for r in valid if r['evaluation']['mean']<global_best-1e-10],
        'prompt_tokens':sum((r.get('usage') or {}).get('prompt_tokens',0) for r in rs),
        'completion_tokens':sum((r.get('usage') or {}).get('completion_tokens',0) for r in rs),
        'reasoning_tokens':sum((r.get('usage') or {}).get('completion_tokens_details',{}).get('reasoning_tokens',0) for r in rs),
        'cost_cny_upper_4_16':sum(r['cost_cny'] for r in rs),
        'cost_cny_list_estimate_3_14':sum(((r.get('usage') or {}).get('prompt_tokens',0)*3+(r.get('usage') or {}).get('completion_tokens',0)*14)/1e6 if r.get('usage') else r['cost_cny'] for r in rs),
        'request_wall_seconds_total':sum(r['wall_seconds'] for r in rs),
        'training_execution_seconds_total':sum(r['evaluation'].get('seconds',0) for r in rs),
        'returned_models':dict(collections.Counter(r.get('returned_model','unknown') for r in rs)),
        'per_parent':per_parent,'equivalent_pairs':pairs,
        'probe_future_useful_rate_correlation_8_parents_descriptive':correlation([r['probe']['useful_rate_all_attempts'] or 0 for r in per_parent],[r['future']['useful_rate_all_attempts'] or 0 for r in per_parent]),
        'warning':'A sampled response mismatch is not proof of unequal stochastic kernels. Correlations across eight parents are confounded by parent quality. Common-bank replays are correlated.'}
    if replay:
        rows=replay['rows']
        dom=[]
        ever_better=False
        for seed in range(100):
            group={r['method']:r for r in rows if r['view']=='attempts' and r['seed']==seed}
            t=group['response']
            dom.append(all(group[m]['train_mean']<=t['train_mean']+1e-10 and group[m]['cost_cny']<t['cost_cny']-1e-12 for m in ['performance','neutral_drift','structural']))
        for view in ['attempts','priced']:
            for seed in range(100):
                group={r['method']:r for r in rows if r['view']==view and r['seed']==seed}
                if group['response']['train_mean']<group['performance']['train_mean']-1e-10:ever_better=True
        gate={'completed_real_attempts':len(rs),'training_only':True,
            'weak_quality_strict_cost_domination_fraction':avg(dom),
            'response_ever_strictly_better_than_performance':ever_better,
            'stop':avg(dom)>=.9 and not ever_better,
            'rule_file_sha256':hashlib.sha256((ROOT/'FUTILITY_GATE.md').read_bytes()).hexdigest(),
            'heldout_results_present_at_gate':(ROOT/'heldout_evaluations.json').exists()}
        details['gate']=gate
        if not (ROOT/'FUTILITY_DECISION.json').exists():save('FUTILITY_DECISION.json',gate)
        detail_rows=[]
        for view in ['attempts','priced']:
            for method in load('config.json')['methods']:
                sub=[r for r in rows if r['view']==view and r['method']==method]
                detail_rows.append({'view':view,'method':method,'mean_train':avg([r['train_mean'] for r in sub]),
                    'mean_attempts':avg([r['attempts'] for r in sub]),'mean_cost_cny':avg([r['cost_cny'] for r in sub]),
                    'pool_exhaustion_fraction':avg([r['pool_exhausted'] for r in sub]),
                    'selected_parent_sets':dict(collections.Counter(','.join(sorted(r['selected_parents'])) for r in sub))})
        details['training_comparisons']=detail_rows
    save('scientific_summary.json',details)
    print(json.dumps({k:v for k,v in details.items() if k not in ['per_parent','equivalent_pairs','training_comparisons']},indent=2))


if __name__=='__main__':main()
