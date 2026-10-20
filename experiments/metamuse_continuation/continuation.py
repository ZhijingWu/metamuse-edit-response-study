"""Targeted prospective-descendant validation. Prior files are read-only.

Only acquire() sends model requests. Generated code uses the previously
validated closed scalar interpreter, never Python source execution.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import importlib.util
import itertools
import json
import math
import os
from pathlib import Path
import random
import statistics
import time
import urllib.error
import urllib.request

ROOT=Path(__file__).resolve().parent
OLD=ROOT.parent/'metamuse_llm_pilot'
spec=importlib.util.spec_from_file_location('validated_pilot',OLD/'llm_pilot.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
METHODS=['performance','random','neutral','performance_cells_short','structural',
    'response_current','response_masked','response_complete','response_local',
    'offspring_quality','probe_control','validity_only']
PROBE_METHODS=set(METHODS)-{'performance','random','neutral','performance_cells_short','structural'}
RESERVE=(8192*4+1200*16)/1e6
MONEY_LIMIT=.062416


def sha(x):return hashlib.sha256(x if isinstance(x,bytes) else x.encode()).hexdigest()
def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def oldread(path):return json.loads((OLD/path).read_text(encoding='utf-8'))
def save(path,x):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8',newline='\n') as f:
        json.dump(x,f,indent=2,ensure_ascii=True,allow_nan=False);f.write('\n')
def textfile(path,s):
    p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8',newline='\n') as f:f.write(s)
def stamp():return time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())
def parents():return {p['id']:p for p in oldread('parents.json')}
def legacy_records():return [json.loads(p.read_text(encoding='utf-8')) for p in sorted((OLD/'calls').glob('*/result.json'))]
def probes():
    return {p:sorted([r for r in legacy_records() if r['parent']==p and r['role']=='probe'],key=lambda r:r['slot']) for p in parents()}
def canonical(p):return (OLD/p['source']).read_text(encoding='utf-8')
def delta(p,r,ps):return [(a-b)/100 for a,b in zip(r['evaluation']['scores'],ps[p]['evaluation']['scores'])]


def descriptor_distance(p,q,mode,ps,pr,penalty=100):
    vals=[]
    for a,b in zip(pr[p],pr[q]):
        if mode=='response_local' and a['edit']!='local':continue
        if mode=='validity_only':
            vals.append((int(a['evaluation']['valid'])-int(b['evaluation']['valid']))**2);continue
        if mode in ['response_masked','response_complete','response_local']:
            if not (a['evaluation']['valid'] and b['evaluation']['valid']):continue
            x,y=delta(p,a,ps),delta(q,b,ps)
        else:
            x=delta(p,a,ps) if a['evaluation']['valid'] else [penalty/100]*12
            y=delta(q,b,ps) if b['evaluation']['valid'] else [penalty/100]*12
        vals.extend((u-v)**2 for u,v in zip(x,y))
    return statistics.mean(vals) if vals else 0.


def select(method,ps,pr,allocation=0):
    ids=sorted(ps);quality=lambda p:(ps[p]['evaluation']['mean'],p)
    if method in ['performance','probe_control']:return sorted(ids,key=quality)[:4]
    if method=='random':return list(list(itertools.combinations(ids,4))[allocation%70])
    if method in ['neutral','performance_cells_short']:
        cells=collections.defaultdict(list)
        for p in ids:cells[tuple(ps[p]['evaluation']['bins'])].append(p)
        groups=sorted(cells.values(),key=lambda g:quality(g[0]))
        if method=='neutral':return list(list(itertools.product(*groups))[allocation%16])
        chosen=[min(g,key=lambda p:(len(canonical(ps[p]).encode()),p)) for g in groups]
        return sorted(chosen,key=quality)[:4]
    if method=='structural':return M.choose('structural',0,ps,pr)
    if method=='offspring_quality':return M.choose('offspring_quality',0,ps,pr)
    eligible=[p for p in ids if method!='response_complete' or all(r['evaluation']['valid'] for r in pr[p])]
    chosen=[min(eligible,key=quality)]
    while len(chosen)<4:
        chosen.append(max((p for p in eligible if p not in chosen),key=lambda p:(min(descriptor_distance(p,q,method,ps,pr) for q in chosen),-quality(p)[0],p)))
    return chosen


def nominal(usage):
    if not usage:return RESERVE
    inp,out=usage['prompt_tokens'],usage['completion_tokens']
    cached=usage.get('prompt_tokens_details',{}).get('cached_tokens',0)
    ip,op,cp=(2,8,.4) if inp<32000 and out<200 else (3,14,.6) if inp<32000 else (4,16,.8)
    return ((inp-cached)*ip+cached*cp+out*op)/1e6


def check_old():
    manifest=oldread('FINAL_MANIFEST.json')
    assert all(sha((OLD/p).read_bytes())==h for p,h in manifest['files'].items())
    return len(manifest['files'])


def prepare():
    if (ROOT/'config.json').exists():raise SystemExit('Frozen continuation already exists')
    n=check_old();ps,pr=parents(),probes()
    selected={m:select(m,ps,pr) for m in METHODS}
    assert selected['performance_cells_short']==['p00','p02','p06','p04'] or set(selected['performance_cells_short'])=={'p00','p02','p04','p06'}
    assert set(selected['response_masked'])=={'p00','p01','p02','p05'}
    assert set(selected['response_local'])==set(selected['response_current'])=={'p00','p01','p05','p06'}
    code_hash=sha(Path(__file__).read_bytes())
    save('MECHANISM_FREEZE.json',{'utc':stamp(),'protocol_sha256':sha((ROOT/'PROTOCOL.md').read_bytes()),
        'script_sha256':code_hash,'selected_sets_for_fixed_selectors':selected,
        'new_heldout_evaluated':False,'new_calls':0,'prior_manifest_files_verified':n})
    traces=[]
    for bank,seed in enumerate(range(20261110,20261118)):
        for t in M.make_traces(seed,True):
            traces.append({**t,'bank':bank,'seed':seed,'name':f'bank{bank}_'+t['name']})
    oldseq={sha(json.dumps(t['items'])) for t in oldread('workloads/train.json')+oldread('workloads/heldout.json')}
    assert not any(sha(json.dumps(t['items'])) in oldseq for t in traces)
    assert len({sha(json.dumps(t['items'])) for t in traces})==96
    save('workloads/new_heldout.json',traces)
    schedule=[]
    for block in range(4):
        rows=[{'logical_id':f'new_{p}_{slot:02}','parent':p,'slot':slot,
            'edit':'local' if slot%2==0 else 'alternative'} for p in sorted(ps) for slot in range(2*block,2*block+2)]
        random.Random(20261071+block).shuffle(rows);schedule.extend(rows)
    save('schedule.json',schedule)
    save('inputs/parents.json',list(ps.values()));save('inputs/probes.json',pr)
    known=[r for r in legacy_records() if r['usage']]
    cfg={'frozen_utc':stamp(),'model':'glm-4.7','endpoint':M.ENDPOINT,
        'temperature':.9,'thinking':{'type':'disabled'},'max_tokens':1200,
        'max_input_reserve_tokens':8192,'max_prompt_ascii_bytes':6000,'timeout_seconds':90,
        'logical_requests':64,'max_additional_attempts':65,'max_transport_retries_total':1,
        'transport_retry_delay_seconds':10,'invalid_generation_retries':0,
        'per_attempt_reserve_cny':RESERVE,'total_reserved_ceiling_cny':65*RESERVE,
        'user_additional_attempt_cap':128,'user_estimated_cny_cap':10,
        'forecast_nominal_including_one_failure':64*statistics.mean(nominal(r['usage']) for r in known)+RESERVE,
        'forecast_conservative_including_one_failure':64*statistics.mean(r['cost_cny'] for r in known)+RESERVE,
        'methods':METHODS,'primary_attempt_budget':32,'priced_budget_cny':MONEY_LIMIT,
        'evaluation_seconds_limit':30,'allocation_draws':560,'new_test_seeds':list(range(20261110,20261118)),
        'system':M.SYSTEM,'edits':M.EDITS,'script_sha256':code_hash,
        'prior_script_sha256':sha((OLD/'llm_pilot.py').read_bytes()),
        'prior_manifest_sha256':sha((OLD/'FINAL_MANIFEST.json').read_bytes()),
        'protocol_sha256':sha((ROOT/'PROTOCOL.md').read_bytes()),
        'new_test_sha256':sha((ROOT/'workloads/new_heldout.json').read_bytes()),
        'train_sha256':sha((OLD/'workloads/train.json').read_bytes()),
        'pricing_source_url':'https://docs.bigmodel.cn/cn/guide/start/pricing.md',
        'pricing_sha256':sha((ROOT/'sources/pricing.md').read_bytes()),
        'credential_source_name':'ANTHROPIC_AUTH_TOKEN (read only in memory)'}
    assert cfg['total_reserved_ceiling_cny']<10 and cfg['max_additional_attempts']<128
    save('config.json',cfg)
    print(json.dumps({'prepared':True,'fixed_sets':selected,'logical_requests':64,'max_attempts':65,
        'max_reserved_cny':65*RESERVE,'new_test_traces':len(traces)}),flush=True)


def attempt_records():
    return [json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'calls').glob('*/result.json'))] if (ROOT/'calls').exists() else []
def logical_records():
    return [json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'logical').glob('*.json'))] if (ROOT/'logical').exists() else []


def ledger():
    rs=attempt_records()
    obj={'new_api_attempts':len(rs),'new_api_responses':sum(r['http_success'] for r in rs),
        'valid_responses':sum(r['evaluation']['valid'] for r in rs),
        'transport_failures':sum(r.get('transport_failure',False) for r in rs),
        'retry_attempts':sum(r['retry'] for r in rs),'logical_completed':len(logical_records()),
        'known_input_tokens':sum((r['usage'] or {}).get('prompt_tokens',0) for r in rs),
        'known_output_tokens':sum((r['usage'] or {}).get('completion_tokens',0) for r in rs),
        'estimated_cny_nominal_plus_failure_reserve':sum(r['nominal_cny'] for r in rs),
        'estimated_cny_conservative_plus_failure_reserve':sum(r['conservative_cny'] for r in rs),
        'unknown_usage_reserves':sum(r['usage'] is None for r in rs),
        'request_wall_seconds':sum(r['wall_seconds'] for r in rs),
        'training_eval_seconds':sum(r['evaluation'].get('seconds',0) for r in rs),
        'total_authorized_reserve_cny':65*RESERVE}
    save('ledger.json',obj);return obj


def acquire(stage):
    cfg=read('config.json')
    assert sha(Path(__file__).read_bytes())==cfg['script_sha256']
    assert sha((OLD/'llm_pilot.py').read_bytes())==cfg['prior_script_sha256']
    if (ROOT/'STOP.json').exists():raise SystemExit('Acquisition previously stopped; no automatic restart')
    start,target=(0,8) if stage=='screen' else (8,64) if stage=='main' else (-1,-1)
    done=logical_records()
    if len(done)!=start:raise SystemExit('Stage boundary mismatch; no automatic restart')
    if stage=='screen' and (ROOT/'calls').exists():raise SystemExit('Attempt records already present')
    if stage=='main' and sum(r['evaluation']['valid'] for r in done)<6:raise SystemExit('Validity screen failed')
    key=os.environ.get('ANTHROPIC_AUTH_TOKEN','')
    if not key:raise SystemExit('Existing credential absent')
    ps=parents();train=oldread('workloads/train.json')
    opener=urllib.request.build_opener(M.NoRedirect)
    for row in read('schedule.json')[start:target]:
        cluster=[]
        for retry in (False,True):
            rs=attempt_records()
            if len(rs)>=65:raise SystemExit('Hard attempt ceiling')
            attempt_id=f'a{len(rs)+1:03}'
            code=canonical(ps[row['parent']])
            prompt=M.EDITS[row['edit']]+'\n\nParent:\n'+code
            assert len((M.SYSTEM+prompt).encode('ascii'))<=6000
            payload={'model':'glm-4.7','messages':[{'role':'system','content':M.SYSTEM},{'role':'user','content':prompt}],
                'max_tokens':1200,'temperature':.9,'thinking':{'type':'disabled'},'stream':False}
            reqdata={**row,'attempt_id':attempt_id,'retry':retry,'started_utc':stamp(),'payload':payload,
                'parent_sha256':ps[row['parent']]['sha256'],'reserved_cny':RESERVE,'endpoint':M.ENDPOINT}
            base='calls/'+attempt_id
            save(base+'/request.json',reqdata)
            r={**row,'attempt_id':attempt_id,'retry':retry,'http_success':False,'transport_failure':False,
                'usage':None,'nominal_cny':RESERVE,'conservative_cny':RESERVE,
                'evaluation':{'valid':False,'reason':'no completed response'}}
            before=time.perf_counter();failure=None
            try:
                request=urllib.request.Request(M.ENDPOINT,data=json.dumps(payload).encode(),method='POST',headers={
                    'Authorization':'Bearer '+key,'Content-Type':'application/json','User-Agent':'metamuse-targeted-continuation/1'})
                with opener.open(request,timeout=90) as response:
                    raw=response.read(200000);r['http_status']=response.status
                raw=raw.replace(key.encode(),b'[REDACTED_CREDENTIAL]')
                (ROOT/base/'response.json').write_bytes(raw)
                data=json.loads(raw);usage=data.get('usage',{})
                inp,out=usage.get('prompt_tokens'),usage.get('completion_tokens')
                if type(inp)!=int or type(out)!=int or not 0<inp<=8192 or not 0<out<=1200:raise M.Invalid('usage accounting/cap violation')
                if data.get('model')!='glm-4.7':raise M.Invalid('returned model differs from frozen model')
                r.update({'http_success':True,'usage':usage,'nominal_cny':nominal(usage),
                    'conservative_cny':(inp*4+out*16)/1e6,'returned_model':data.get('model'),
                    'response_id':data.get('id'),'finish_reason':data['choices'][0].get('finish_reason')})
                content=data['choices'][0]['message'].get('content') or ''
                textfile(base+'/content.txt',content)
                try:
                    source=M.extract_source(content);textfile(base+'/program.py',source)
                    r['program_sha256']=sha(source);r['evaluation']=M.evaluate(source,train)
                except Exception as e:
                    r['evaluation']={'valid':False,'reason':(type(e).__name__+': '+str(e)).replace(key,'[REDACTED]')[:180]}
            except urllib.error.HTTPError as e:
                raw=e.read(20000).replace(key.encode(),b'[REDACTED_CREDENTIAL]')
                (ROOT/base/'error_response.txt').write_bytes(raw)
                r['http_status']=e.code;failure='HTTP '+str(e.code)
            except (urllib.error.URLError,TimeoutError,ConnectionError,OSError) as e:
                r['transport_failure']=True;failure=(type(e).__name__+': '+str(e)).replace(key,'[REDACTED]')[:200]
            except Exception as e:
                failure=(type(e).__name__+': '+str(e)).replace(key,'[REDACTED]')[:200]
            if failure:r['evaluation']={'valid':False,'reason':failure}
            r['wall_seconds']=time.perf_counter()-before;r['finished_utc']=stamp()
            save(base+'/result.json',r);cluster.append(r)
            state=ledger()
            print(json.dumps({'attempt':state['new_api_attempts'],'logical':row['logical_id'],
                'retry':retry,'http_success':r['http_success'],'valid':r['evaluation']['valid'],
                'mean':r['evaluation'].get('mean'),'reason':r['evaluation'].get('reason'),
                'conservative_cny_total':state['estimated_cny_conservative_plus_failure_reserve']}),flush=True)
            if not failure:
                save('logical/'+row['logical_id']+'.json',{**row,'attempt_ids':[x['attempt_id'] for x in cluster],
                    'final_attempt_id':attempt_id,'evaluation':r['evaluation'],'program_sha256':r.get('program_sha256')})
                ledger();break
            if r['transport_failure'] and state['transport_failures']==1 and not retry:
                time.sleep(10);continue
            save('STOP.json',{'utc':stamp(),'reason':failure,'at_attempt':attempt_id,
                'completed_logical':len(logical_records()),'no_additional_requests':True})
            raise SystemExit('Frozen failure stop; no further calls')
    if stage=='screen':
        valid=sum(r['evaluation']['valid'] for r in logical_records())
        save('SCREEN.json',{'utc':stamp(),'logical_requests':8,'valid':valid,'passed':valid>=6})
        if valid<6:
            save('STOP.json',{'utc':stamp(),'reason':'first-eight validity below 6/8'});raise SystemExit('Validity stop')


def legacy_event(r):
    return {'event_id':'legacy_'+r['id'],'candidate_id':r['id'],
        'parent':r['parent'],'role':'probe','nominal_cny':nominal(r['usage']),
        'conservative_cny':r['cost_cny'],'wall_seconds':r['wall_seconds'],
        'evaluation':r['evaluation'],'source_root':'prior',
        'source_path':'calls/'+r['id']+'/program.py'}


def events_for(method,chosen,allocation,ps,pr,logical,attempts):
    events=[]
    if method in PROBE_METHODS:
        pitems=[r for p in sorted(pr) for r in pr[p] if method!='response_local' or r['edit']=='local']
        events.extend(legacy_event(r) for r in sorted(pitems,key=lambda r:r['id']))
    byparent={p:[] for p in ps}
    for p in ps:
        label_lists=[]
        for label in ['local','alternative']:
            seq=sorted([r for r in logical if r['parent']==p and r['edit']==label],key=lambda r:r['slot'])
            random.Random(20264000+allocation*31+int(p[1:])*2+(label=='alternative')).shuffle(seq)
            label_lists.append(seq)
        for k in range(max([len(x) for x in label_lists]+[0])):
            for seq in label_lists:
                if k<len(seq):byparent[p].append(seq[k])
    order=list(chosen);random.Random(20265000+allocation).shuffle(order)
    for k in range(max([len(byparent[p]) for p in chosen]+[0])):
        for p in order:
            if k>=len(byparent[p]):continue
            for aid in byparent[p][k]['attempt_ids']:
                r=attempts[aid]
                events.append({'event_id':aid,'candidate_id':r['logical_id'],
                    'parent':p,'role':'fresh_future','nominal_cny':r['nominal_cny'],
                    'conservative_cny':r['conservative_cny'],'wall_seconds':r['wall_seconds'],
                    'evaluation':r['evaluation'],'source_root':'continuation',
                    'source_path':'calls/'+aid+'/program.py'})
    return events


def replay():
    if (ROOT/'selection_freeze.json').exists():raise SystemExit('Selection already frozen; do not overwrite')
    ps,pr=parents(),probes();logical=logical_records();ats={r['attempt_id']:r for r in attempt_records()}
    shared_seed_seconds=sum(p['evaluation']['seconds'] for p in ps.values())
    initial=min(ps,key=lambda p:(ps[p]['evaluation']['mean'],p))
    rows=[];event_catalog={};selection_times={}
    for allocation in range(560):
        for method in METHODS:
            st=time.perf_counter();chosen=select(method,ps,pr,allocation);selector_seconds=time.perf_counter()-st
            selection_times.setdefault(method,[]).append(selector_seconds)
            events=events_for(method,chosen,allocation,ps,pr,logical,ats)
            for e in events:event_catalog[e['event_id']]=e
            for view,credits in [('credits',8),('credits',16),('credits',24),('credits',32),('priced',32)]:
                best=initial;bestval=ps[initial]['evaluation']['mean'];used=[];cost=0;cons=0;secs=shared_seed_seconds+selector_seconds;wall=0
                stopped='pool'
                for e in events:
                    if len(used)>=credits:stopped='attempt_budget';break
                    if view=='priced' and cost+e['nominal_cny']>MONEY_LIMIT+1e-12:stopped='money_budget';break
                    next_secs=secs+e['evaluation'].get('seconds',0)
                    if view=='priced' and next_secs>30:stopped='evaluation_time_budget';break
                    used.append(e['event_id']);cost+=e['nominal_cny'];cons+=e['conservative_cny'];secs=next_secs;wall+=e['wall_seconds']
                    ev=e['evaluation']
                    if ev['valid'] and (ev['mean'],e['candidate_id'])<(bestval,best):best,bestval=e['candidate_id'],ev['mean']
                if len(used)==credits:stopped='attempt_budget'
                rows.append({'allocation':allocation,'method':method,'view':view,'budget_attempts':credits,
                    'parents':chosen,'best_id':best,'train_mean':bestval,'events':used,'attempts':len(used),
                    'nominal_cny':cost,'conservative_cny':cons,'evaluation_seconds_including_common':secs,
                    'reconstructed_request_wall_seconds':wall,'stop_reason':stopped,
                    'pool_censored':stopped=='pool' and len(used)<credits})
    save('replay_training.json',{'utc':stamp(),'new_logical_completed':len(logical),
        'heldout_accessed':False,'rows':rows,'event_catalog':event_catalog,
        'allocation_is_not_independent_model_experiment':True,
        'selector_computation_seconds_total':{k:sum(v) for k,v in selection_times.items()}})
    save('selection_freeze.json',{'utc':stamp(),'new_logical_completed':len(logical),
        'new_api_attempts':len(ats),'replay_sha256':sha((ROOT/'replay_training.json').read_bytes()),
        'config_sha256':sha((ROOT/'config.json').read_bytes()),
        'new_heldout_results_present':(ROOT/'heldout_results.json').exists(),
        'no_further_paid_requests':True})
    print(json.dumps({'rows':len(rows),'new_logical_completed':len(logical),
        'primary_pool_censored':sum(r['pool_censored'] for r in rows if r['budget_attempts']==32),
        'new_heldout_read':False}),flush=True)


def heldout():
    if (ROOT/'heldout_results.json').exists():raise SystemExit('New heldout already evaluated; no overwrite')
    freeze=read('selection_freeze.json')
    assert sha((ROOT/'replay_training.json').read_bytes())==freeze['replay_sha256']
    assert sha((ROOT/'workloads/new_heldout.json').read_bytes())==read('config.json')['new_test_sha256']
    replay_data=read('replay_training.json');traces=read('workloads/new_heldout.json');ps=parents()
    # Evaluate only training-selected outputs and prespecified seed/old-champion
    # references. No heldout selection is used to reduce training search cost.
    sources={p:('prior',ps[p]['source']) for p in ps}
    for e in replay_data['event_catalog'].values():
        if e['evaluation']['valid']:sources[e['candidate_id']]=(e['source_root'],e['source_path'])
    sources['old_champion_reference']=('prior','calls/future_p06_02/program.py')
    selected={r['best_id'] for r in replay_data['rows']}|set(ps)|{'old_champion_reference'}
    cache={};results={}
    for cid in sorted(selected):
        where,path=sources[cid];source=((OLD if where=='prior' else ROOT)/path).read_text(encoding='utf-8');key=sha(source)
        if key not in cache:
            pertrace=[]
            for t in traces:
                ev=M.evaluate(source,[t])
                pertrace.append({'trace':t['name'],'bank':t['bank'],'family':t['family'],'valid':ev['valid'],
                    'score':ev['mean'] if ev['valid'] else 100*(192-t['l1_bound'])/t['l1_bound'],
                    'invalid_penalty_used':not ev['valid'],'reason':ev.get('reason'),
                    'bins':ev['bins'][0] if ev['valid'] else None,'seconds':ev['seconds']})
            cache[key]={'all_valid':all(e['valid'] for e in pertrace),'mean':statistics.mean(e['score'] for e in pertrace),
                'bank_means':[statistics.mean(e['score'] for e in pertrace if e['bank']==b) for b in range(8)],
                'per_trace':pertrace,'source_sha256':key}
        results[cid]=cache[key]
        print(json.dumps({'heldout_candidate':cid,'mean':results[cid]['mean'],'valid':results[cid]['all_valid']}),flush=True)
    save('heldout_results.json',{'utc':stamp(),'selection_sha256':freeze['replay_sha256'],
        'test_sha256':read('config.json')['new_test_sha256'],'evaluations':results,
        'evaluated_unique_sources':len(cache),'fresh_traces':96,'independent_workload_banks':8,
        'model_search_banks':1,'no_new_generation_after_test':True})


def main():
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['prepare','acquire','replay','heldout']);ap.add_argument('--stage')
    a=ap.parse_args()
    if a.command=='prepare':prepare()
    elif a.command=='acquire':acquire(a.stage)
    elif a.command=='replay':replay()
    else:heldout()


if __name__=='__main__':main()
