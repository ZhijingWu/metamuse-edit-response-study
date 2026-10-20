"""Bounded real-LLM BPP pilot. Generated source is interpreted, never exec'd.

Only the acquire command can call the model. Evaluation cannot access secrets.
All paths are confined to this new experiment directory.
"""
from __future__ import annotations
import argparse
import ast
import collections
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import statistics
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
ARGS = ['remaining', 'item', 'capacity', 'index', 'n_bins']
ENDPOINT = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
RESERVE = (8192 * 4 + 1200 * 16) / 1e6
SYSTEM = '''You edit deterministic executable online bin-packing heuristics.
Return only Python source defining score(remaining, item, capacity, index, n_bins).
For each feasible existing bin, this function returns a finite numeric priority;
the highest priority wins, ties use the lowest bin index. New bins are forced
only when no existing bin fits. capacity=100; remaining>=item>0; indices start at 0.
Use only numeric constants, local scalar assignments, if/elif/else, return,
arithmetic + - * / // % ** (power at most 4), comparisons, boolean operators,
conditional expressions, and calls to abs, min, max, exp, log, sqrt.
No imports, attributes, subscripts, loops, comprehensions, collections, globals,
recursion, randomness, annotations, decorators, strings or extra functions.
Keep source under 1600 ASCII characters. Avoid division by zero and huge values.
The objective is fewer bins on unseen online sequences, not prettier code.
The training workload families are uniform, Weibull, complementary and phased
sizes. No future items or sequence history are available to this scorer.
Produce a genuinely changed scoring algorithm, not a rename or scaling alone.'''
EDITS = {
 'local': 'Improve this parent by making a targeted nonlinear or conditional change to its bin-scoring rule. Retain a recognizable connection to its rationale, but seek better packing.',
 'alternative': 'Improve this parent by proposing a different residual-space scoring tradeoff, possibly using item size or current bin population. You may change its main scoring preference.',
}
METHODS = ['performance', 'random', 'neutral_drift', 'structural', 'response', 'probe_control', 'offspring_quality']


def dump(path, obj):
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=True, allow_nan=False) + '\n', encoding='utf-8')


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def sha(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode()).hexdigest()


def stamp():
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())


class Invalid(ValueError):
    pass


class Returned(Exception):
    def __init__(self, value):
        self.value = value


def number(x):
    if type(x) not in (int, float, bool) or not math.isfinite(x) or abs(x) > 1e12:
        raise Invalid('non-finite, non-scalar or oversized numeric value')
    return x


class ScalarProgram:
    """A closed scalar language, with no host Python object or global access."""
    allowed = (ast.Module, ast.FunctionDef, ast.arguments, ast.arg, ast.Assign,
        ast.Name, ast.Load, ast.Store, ast.Constant, ast.If, ast.Return,
        ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod,
        ast.Pow, ast.UnaryOp, ast.UAdd, ast.USub, ast.Not, ast.Compare,
        ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq, ast.BoolOp,
        ast.And, ast.Or, ast.IfExp, ast.Call)
    functions = {'abs', 'min', 'max', 'exp', 'log', 'sqrt'}

    def __init__(self, source):
        if len(source.encode('utf-8')) > 6000:
            raise Invalid('source size')
        tree = ast.parse(source)
        nodes = list(ast.walk(tree))
        if len(nodes) > 400 or any(not isinstance(n, self.allowed) for n in nodes):
            raise Invalid('unsupported syntax or AST size')
        if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
            raise Invalid('exactly one function required')
        f = tree.body[0]
        a = f.args
        if (f.name != 'score' or [x.arg for x in a.args] != ARGS or f.decorator_list
            or f.returns or a.posonlyargs or a.kwonlyargs or a.vararg or a.kwarg
            or a.defaults or a.kw_defaults or any(x.annotation for x in a.args)):
            raise Invalid('function contract')
        for n in nodes:
            if isinstance(n, ast.Constant):
                number(n.value)
            if isinstance(n, ast.Name) and (n.id.startswith('_') or len(n.id) > 64):
                raise Invalid('name restriction')
            if isinstance(n, ast.Assign):
                if len(n.targets) != 1 or not isinstance(n.targets[0], ast.Name):
                    raise Invalid('scalar assignment required')
                if n.targets[0].id in self.functions:
                    raise Invalid('reserved function name')
            if isinstance(n, ast.Call):
                if not isinstance(n.func, ast.Name) or n.func.id not in self.functions or n.keywords or not 1 <= len(n.args) <= 8:
                    raise Invalid('call restriction')
        self.body = f.body
        self.features = collections.Counter(type(n).__name__ for n in nodes)

    def __call__(self, *args):
        env = dict(zip(ARGS, args))
        self.steps = 0
        try:
            self.block(self.body, env)
        except Returned as r:
            return number(r.value)
        raise Invalid('missing return')

    def tick(self):
        self.steps += 1
        if self.steps > 1024:
            raise Invalid('instruction budget')

    def block(self, body, env):
        for n in body:
            self.tick()
            if isinstance(n, ast.Return):
                raise Returned(self.expr(n.value, env))
            if isinstance(n, ast.Assign):
                env[n.targets[0].id] = self.expr(n.value, env)
            elif isinstance(n, ast.If):
                self.block(n.body if self.expr(n.test, env) else n.orelse, env)

    def expr(self, n, env):
        self.tick()
        if isinstance(n, ast.Constant):
            return n.value
        if isinstance(n, ast.Name):
            if n.id not in env:
                raise Invalid('unknown variable')
            return env[n.id]
        if isinstance(n, ast.IfExp):
            return self.expr(n.body if self.expr(n.test, env) else n.orelse, env)
        if isinstance(n, ast.BoolOp):
            v = self.expr(n.values[0], env)
            for sub in n.values[1:]:
                if isinstance(n.op, ast.And) and not v or isinstance(n.op, ast.Or) and v:
                    break
                v = self.expr(sub, env)
            return v
        if isinstance(n, ast.UnaryOp):
            v = self.expr(n.operand, env)
            return number(-v if isinstance(n.op, ast.USub) else +v if isinstance(n.op, ast.UAdd) else not v)
        if isinstance(n, ast.BinOp):
            a, b = self.expr(n.left, env), self.expr(n.right, env)
            op = n.op
            if isinstance(op, ast.Add): v = a+b
            elif isinstance(op, ast.Sub): v = a-b
            elif isinstance(op, ast.Mult): v = a*b
            elif isinstance(op, ast.Div): v = a/b
            elif isinstance(op, ast.FloorDiv): v = a//b
            elif isinstance(op, ast.Mod): v = a%b
            elif isinstance(op, ast.Pow):
                if abs(b) > 4: raise Invalid('power bound')
                v = a**b
            else: raise Invalid('operator')
            return number(v)
        if isinstance(n, ast.Compare):
            a = self.expr(n.left, env)
            for op, right in zip(n.ops, n.comparators):
                b = self.expr(right, env)
                if isinstance(op, ast.Lt): ok = a < b
                elif isinstance(op, ast.LtE): ok = a <= b
                elif isinstance(op, ast.Gt): ok = a > b
                elif isinstance(op, ast.GtE): ok = a >= b
                elif isinstance(op, ast.Eq): ok = a == b
                elif isinstance(op, ast.NotEq): ok = a != b
                else: raise Invalid('comparison')
                if not ok: return False
                a = b
            return True
        if isinstance(n, ast.Call):
            vals = [self.expr(a, env) for a in n.args]
            name = n.func.id
            if name == 'abs': v = abs(*vals)
            elif name == 'min': v = min(vals)
            elif name == 'max': v = max(vals)
            elif name == 'exp':
                if len(vals) != 1 or abs(vals[0]) > 25: raise Invalid('exp bound')
                v = math.exp(vals[0])
            elif name == 'log': v = math.log(*vals)
            elif name == 'sqrt': v = math.sqrt(*vals)
            else: raise Invalid('function')
            return number(v)
        raise Invalid('expression')


def make_traces(seed, shifted):
    rng = random.Random(seed)
    traces = []
    n = 192
    for family in ('uniform', 'weibull', 'complementary', 'phased'):
        for rep in range(3):
            if family == 'uniform':
                items = [rng.randint(15 if shifted else 5, 85 if shifted else 95) for _ in range(n)]
            elif family == 'weibull':
                items = [min(100, max(1, round(rng.weibullvariate(35, 2.5 if shifted else 1.5)))) for _ in range(n)]
            elif family == 'complementary':
                k = 40 if shifted else 25
                items = [rng.choice((k, 100-k))+rng.randint(-4, 4) for _ in range(n)]
            else:
                lo = [rng.randint(10, 35) for _ in range(n//2)]
                hi = [rng.randint(55, 85) for _ in range(n//2)]
                items = hi+lo if shifted else lo+hi
            traces.append({'name': f'{family}_{rep}', 'family': family, 'items': items,
                'l1_bound': math.ceil(sum(items)/100), 'capacity': 100})
    return traces


def packing(program, items):
    remaining = []
    actions = []
    for item in items:
        candidates = []
        for i, rem in enumerate(remaining):
            if rem >= item:
                candidates.append((program(rem, item, 100, i, len(remaining)), -i))
        chosen = -max(candidates)[1] if candidates else -1
        if chosen == -1:
            remaining.append(100-item)
        else:
            remaining[chosen] -= item
        actions.append(chosen)
    if not all(0 <= r < 100 for r in remaining) or 100*len(remaining)-sum(remaining) != sum(items):
        raise Invalid('packing invariants')
    return len(remaining), sha(json.dumps(actions))


def evaluate(source, traces):
    start = time.perf_counter()
    try:
        p = ScalarProgram(source)
        bins, actions = [], []
        for t in traces:
            b, a = packing(p, t['items'])
            if b < t['l1_bound']: raise Invalid('lower bound')
            bins.append(b); actions.append(a)
            if time.perf_counter()-start > 20: raise Invalid('evaluation wall limit')
        scores = [100*(b-t['l1_bound'])/t['l1_bound'] for b,t in zip(bins,traces)]
        return {'valid': True, 'bins': bins, 'scores': scores,
            'mean': statistics.mean(scores), 'action_hashes': actions,
            'features': dict(p.features), 'seconds': time.perf_counter()-start}
    except Exception as e:
        return {'valid': False, 'reason': type(e).__name__ + ': ' + str(e)[:160],
            'seconds': time.perf_counter()-start}


def prepare():
    if (ROOT/'config.json').exists(): raise SystemExit('Existing frozen config: not overwritten')
    expressions = ['-(remaining-item)', '1.0/(remaining-item+1)', '-index',
        '1.0/(index+1)', 'remaining-item', '(remaining-item)/capacity',
        '-abs(remaining-item-20)', '-((remaining-item-20)*(remaining-item-20))']
    names = ['best_fit_gap','best_fit_reciprocal','first_fit_index','first_fit_reciprocal',
        'worst_fit_gap','worst_fit_fraction','target_absolute','target_squared']
    train, test = make_traces(20261040, False), make_traces(20261041, True)
    dump('workloads/train.json', train); dump('workloads/heldout.json', test)
    parents = []
    for i, (ex, name) in enumerate(zip(expressions,names)):
        source = 'def score('+', '.join(ARGS)+'):\n    return '+ex+'\n'
        pid = f'p{i:02}'
        path = 'parents/'+pid+'.py'
        (ROOT/path).parent.mkdir(exist_ok=True)
        (ROOT/path).write_text(source, encoding='utf-8')
        parents.append({'id':pid, 'name':name, 'source':path, 'sha256':sha(source),
            'provenance':'human implementation of named elementary heuristic',
            'evaluation':evaluate(source,train)})
    assert all(p['evaluation']['valid'] for p in parents)
    for i in range(0,8,2):
        assert parents[i]['evaluation']['bins'] == parents[i+1]['evaluation']['bins']
        assert parents[i]['evaluation']['action_hashes'] == parents[i+1]['evaluation']['action_hashes']
    # Verify evaluator against direct familiar decisions, without running generated code.
    conformance = []
    for i in (0,2,4,6):
        for t in train:
            bins=[]
            for item in t['items']:
                fit=[j for j,r in enumerate(bins) if r>=item]
                if not fit: bins.append(100-item); continue
                if i==0: j=min(fit,key=lambda j:(bins[j]-item,j))
                elif i==2: j=fit[0]
                elif i==4: j=min(fit,key=lambda j:(-(bins[j]-item),j))
                else: j=min(fit,key=lambda j:(abs(bins[j]-item-20),j))
                bins[j]-=item
            assert len(bins)==parents[i]['evaluation']['bins'][len(conformance)%12]
            conformance.append({'parent':i,'trace':t['name'],'bins':len(bins)})
    denials = ['import os\n', 'def score('+', '.join(ARGS)+'):\n    return remaining.__class__\n',
        'def score('+', '.join(ARGS)+'):\n    while True: pass\n',
        'def score('+', '.join(ARGS)+'):\n    return open(1)\n',
        'def score('+', '.join(ARGS)+'):\n    return 10**1000000\n']
    for s in denials:
        assert not evaluate(s,train)['valid']
    dump('parents.json',parents)
    schedule=[]
    for role, slots in [('probe',range(2)),('future',range(12))]:
        rows=[{'id': f'{role}_{p["id"]}_{s:02}', 'parent':p['id'], 'role':role,
               'slot':s, 'edit':'local' if s%2==0 else 'alternative'} for p in parents for s in slots]
        if role=='probe':
            random.Random(20261042).shuffle(rows); schedule+=rows
        else:
            for group in range(3):
                batch=[r for r in rows if r['slot']//4==group]
                random.Random(20261043+group).shuffle(batch); schedule+=batch
    dump('schedule.json',schedule)
    dump('config.json',{'frozen_utc':stamp(),'model':'glm-4.7','endpoint':ENDPOINT,
        'credential_source':'process environment ANTHROPIC_AUTH_TOKEN; not serialized',
        'max_attempts':112,'max_successes':112,'max_tokens':1200,'input_reserve_tokens':8192,
        'max_prompt_bytes':6000,'timeout_seconds':90,'retries':0,'temperature':0.9,
        'thinking':{'type':'disabled'},'prices_cny_per_million':{'input':4,'output':16},
        'reservation_per_attempt_cny':RESERVE,'max_reserved_cny':112*RESERVE,
        'usd_envelope':25,'conservative_usd_per_cny':1,'methods':METHODS,
        'archive_size':4,'attempts_per_replay':48,'replay_seeds':100,
        'system':SYSTEM,'edits':EDITS,'protocol_sha256':sha((ROOT/'PROTOCOL.md').read_bytes()),
        'script_sha256':sha(Path(__file__).read_bytes()),'python':platform.python_version(),
        'workload_train_sha256':sha((ROOT/'workloads/train.json').read_bytes()),
        'workload_heldout_sha256':sha((ROOT/'workloads/heldout.json').read_bytes())})
    dump('validation_preflight.json',{'conformance_cases':conformance,'unsafe_denials':len(denials),
        'equivalent_pairs':4,'all_valid':True,'source_execution':'closed AST interpreter only'})
    print(json.dumps({'prepared':True,'parent_training_means':{p['id']:p['evaluation']['mean'] for p in parents},'reserve_cny':112*RESERVE}),flush=True)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):
        raise Invalid('HTTP redirect refused')


def attempts():
    return sorted((ROOT/'calls').glob('*/request.json')) if (ROOT/'calls').exists() else []


def records():
    return [json.loads(p.read_text(encoding='utf-8')) for p in sorted((ROOT/'calls').glob('*/result.json'))] if (ROOT/'calls').exists() else []


def extract_source(content):
    s=content.strip()
    if '```' in s:
        blocks=s.split('```')
        if len(blocks)!=3: raise Invalid('exactly one closed code block required')
        lines=blocks[1].splitlines()
        if lines[0].strip() not in ('python',''): raise Invalid('Python code block required')
        s='\n'.join(lines[1:])+'\n'
    ScalarProgram(s)
    return s


def acquire(stage):
    cfg=read('config.json')
    if sha(Path(__file__).read_bytes())!=cfg['script_sha256']: raise SystemExit('Frozen acquisition code differs')
    if stage not in ['calibration','probes','future1','future2','future3']: raise SystemExit('stage')
    ceiling={'calibration':4,'probes':16,'future1':48,'future2':80,'future3':112}[stage]
    minimum={'calibration':0,'probes':4,'future1':16,'future2':48,'future3':80}[stage]
    current=len(attempts())
    if current!=minimum: raise SystemExit('Stage start mismatch; no automatic resumption/retry')
    if minimum:
        previous=records()
        if len(previous)!=current or any(not r.get('http_success') for r in previous): raise SystemExit('Earlier infrastructure failure; stop')
        if stage=='probes' and sum(r['evaluation']['valid'] for r in previous)<3: raise SystemExit('Calibration validity below 3/4')
        if stage=='future1':
            if sum(r['evaluation']['valid'] for r in previous)<12: raise SystemExit('Probe validity below 12/16')
            parentmap={p['id']:p for p in read('parents.json')}
            useful={r.get('program_sha256') for r in previous if r['evaluation']['valid'] and r['evaluation']['mean']<parentmap[r['parent']]['evaluation']['mean']-1e-10}
            if len(useful)<2: raise SystemExit('Fewer than two distinct useful probe children; stop')
        if stage in ['future2','future3'] and (ROOT/'training_replay.json').exists():
            if read('training_replay.json')['early_domination_stop']: raise SystemExit('Cheap baselines dominate training; stop')
    key=os.environ.get('ANTHROPIC_AUTH_TOKEN','')
    if not key: raise SystemExit('Configured credential unavailable')
    if 112*RESERVE>25: raise SystemExit('Envelope preflight')
    opener=urllib.request.build_opener(NoRedirect)
    parentmap={p['id']:p for p in read('parents.json')}
    train=read('workloads/train.json')
    for row in read('schedule.json')[current:ceiling]:
        if len(attempts())>=112: raise SystemExit('Attempt limit')
        code=(ROOT/parentmap[row['parent']]['source']).read_text(encoding='utf-8')
        prompt=EDITS[row['edit']]+'\n\nParent:\n'+code
        if len((SYSTEM+prompt).encode('ascii'))>6000: raise SystemExit('Input reservation exceeded')
        payload={'model':'glm-4.7','messages':[{'role':'system','content':SYSTEM},{'role':'user','content':prompt}],
            'max_tokens':1200,'temperature':0.9,'thinking':{'type':'disabled'},'stream':False}
        request={**row,'started_utc':stamp(),'payload':payload,'reservation_cny':RESERVE,
            'endpoint':ENDPOINT,'parent_sha256':parentmap[row['parent']]['sha256']}
        directory='calls/'+row['id']
        dump(directory+'/request.json',request) # Reserve and persist BEFORE network.
        started=time.perf_counter(); raw=b''
        result={**row,'http_success':False,'evaluation':{'valid':False,'reason':'no completed response'},'usage':None,'cost_cny':RESERVE}
        try:
            req=urllib.request.Request(ENDPOINT,data=json.dumps(payload).encode(),method='POST',headers={
                'Authorization':'Bearer '+key,'Content-Type':'application/json','User-Agent':'metamuse-bounded-research/1'})
            with opener.open(req,timeout=90) as response:
                raw=response.read(200000)
                result['http_status']=response.status
            # Never write a credential even if a server accidentally echoes it.
            raw=raw.replace(key.encode(),b'[REDACTED_CREDENTIAL]')
            (ROOT/directory/'response.json').write_bytes(raw)
            data=json.loads(raw)
            usage=data.get('usage',{})
            inp,out=usage.get('prompt_tokens'),usage.get('completion_tokens')
            if type(inp)!=int or type(out)!=int or inp<=0 or out<=0: raise Invalid('missing usage accounting')
            if inp>8192 or out>1200: raise Invalid('usage exceeds token reservation')
            result.update({'http_success':True,'usage':usage,'cost_cny':(inp*4+out*16)/1e6,
                'returned_model':data.get('model'),'response_id':data.get('id'),
                'finish_reason':data['choices'][0].get('finish_reason')})
            text=data['choices'][0]['message'].get('content') or ''
            (ROOT/directory/'content.txt').write_text(text,encoding='utf-8')
            source=extract_source(text)
            (ROOT/directory/'program.py').write_text(source,encoding='utf-8')
            result['program_sha256']=sha(source)
            result['evaluation']=evaluate(source,train)
        except urllib.error.HTTPError as e:
            result['http_status']=e.code
            raw=e.read(20000).replace(key.encode(),b'[REDACTED_CREDENTIAL]')
            (ROOT/directory/'error_response.txt').write_bytes(raw)
            result['evaluation']={'valid':False,'reason':'HTTP '+str(e.code)}
        except Exception as e:
            # Error strings are sanitized before persistence, never print headers.
            result['evaluation']={'valid':False,'reason':(type(e).__name__+': '+str(e)).replace(key,'[REDACTED_CREDENTIAL]')[:200]}
        result['wall_seconds']=time.perf_counter()-started
        result['finished_utc']=stamp()
        dump(directory+'/result.json',result)
        rs=records()
        dump('ledger.json',{'attempts':len(attempts()),'http_successes':sum(r['http_success'] for r in rs),
            'valid_programs':sum(r['evaluation']['valid'] for r in rs),'cost_cny_conservative':sum(r['cost_cny'] for r in rs),
            'unknown_usage_calls':sum(r['usage'] is None for r in rs),'max_reserved_cny':len(attempts())*RESERVE,
            'successful_edit_limit':128,'authorized_usd_limit':25,'usd_upper_bound_at_1_to_1':sum(r['cost_cny'] for r in rs)})
        print(json.dumps({'attempt':len(attempts()),'id':row['id'],'http_success':result['http_success'],
            'valid':result['evaluation']['valid'],'mean':result['evaluation'].get('mean'),
            'reason':result['evaluation'].get('reason'),'seconds':round(result['wall_seconds'],2),'cost_cny':result['cost_cny']}),flush=True)
        if not result['http_success']: raise SystemExit('Infrastructure/accounting failure: no retry or endpoint fallback')
    if stage=='calibration':
        rs=records()
        dump('calibration.json',{'completed_utc':stamp(),'count':len(rs),'valid':sum(r['evaluation']['valid'] for r in rs),
            'mean_cost_cny':statistics.mean(r['cost_cny'] for r in rs),
            'primary_replay_cost_budget_cny':32*statistics.mean(r['cost_cny'] for r in rs),
            'reason':'price calibration only; fixed before future outcomes and selection replay'})


def dist(a,b):
    return sum((x-y)**2 for x,y in zip(a,b))/max(1,len(a))


def choose(method, seed, parents, probes):
    rng=random.Random(seed)
    ids=sorted(parents)
    quality=lambda p:(parents[p]['evaluation']['mean'],p)
    if method in ['performance','probe_control']: return sorted(ids,key=quality)[:4]
    if method=='random': return sorted(rng.sample(ids,4))
    if method=='neutral_drift':
        order=ids[:];rng.shuffle(order)
        cells={}
        for p in order:cells[tuple(parents[p]['evaluation']['bins'])]=p
        chosen=sorted(cells.values(),key=quality)[:4]
        for p in reversed(order):
            if len(chosen)==4:break
            if p not in chosen:chosen.append(p)
        return sorted(chosen)
    if method=='offspring_quality':
        return sorted(ids,key=lambda p:(statistics.mean(r['evaluation'].get('mean',parents[p]['evaluation']['mean']+100) for r in probes[p]),quality(p)))[:4]
    if method=='structural':
        keys=sorted({k for p in ids for k in parents[p]['evaluation']['features']})
        feats={p:[parents[p]['evaluation']['features'].get(k,0)/sum(parents[p]['evaluation']['features'].values()) for k in keys] for p in ids}
    elif method=='response':
        feats={}
        for p in ids:
            feats[p]=[]
            for r in sorted(probes[p],key=lambda r:r['slot']):
                base=parents[p]['evaluation']['scores']
                child=r['evaluation'].get('scores',[x+100 for x in base])
                feats[p]+=[(a-b)/100 for a,b in zip(child,base)]
    else:raise Invalid('method')
    chosen=[min(ids,key=quality)]
    while len(chosen)<4:
        chosen.append(max((p for p in ids if p not in chosen),key=lambda p:(min(dist(feats[p],feats[q]) for q in chosen),-quality(p)[0],p)))
    return chosen


def replay():
    ps={p['id']:p for p in read('parents.json')}
    rs=records()
    probes={p:sorted([r for r in rs if r['parent']==p and r['role']=='probe'],key=lambda r:r['slot']) for p in ps}
    if any(len(x)!=2 for x in probes.values()): raise SystemExit('Need all probe outcomes for comparison')
    future={p:[r for r in rs if r['parent']==p and r['role']=='future'] for p in ps}
    rows=[]
    for seed in range(100):
        for method in METHODS:
            selected=choose(method,seed,ps,probes)
            future_order={}
            for p in ps:
                seq=sorted(future[p],key=lambda r:r['slot'])
                random.Random(20262000+seed).shuffle(seq)
                future_order[p]=seq
            rng=random.Random(seed+20263000); order=selected[:];rng.shuffle(order)
            events=[]
            if method in ['response','probe_control','offspring_quality']:
                events=[r for r in rs if r['role']=='probe']
                events.sort(key=lambda r:r['id'])
            for j in range(max([len(future_order[p]) for p in selected]+[0])):
                for p in order:
                    if j<len(future_order[p]):events.append(future_order[p][j])
            for view in ['attempts','priced']:
                best=min(ps,key=lambda p:(ps[p]['evaluation']['mean'],p))
                bestval=ps[best]['evaluation']['mean']
                cost=0; used=[]; evaluation_seconds=0
                limit=read('calibration.json')['primary_replay_cost_budget_cny']
                for r in events:
                    if len(used)>=48 or view=='priced' and cost+r['cost_cny']>limit+1e-12:break
                    cost+=r['cost_cny'];used.append(r['id']);evaluation_seconds+=r['evaluation'].get('seconds',0)
                    e=r['evaluation']
                    if e['valid'] and (e['mean'],r['id'])<(bestval,best):best,bestval=r['id'],e['mean']
                rows.append({'seed':seed,'method':method,'view':view,'selected_parents':selected,
                    'best_id':best,'train_mean':bestval,'events':used,'attempts':len(used),'cost_cny':cost,
                    'cost_limit_cny':limit if view=='priced' else None,'unused_cost_cny':max(0,limit-cost) if view=='priced' else None,
                    'evaluation_seconds':evaluation_seconds,'pool_exhausted':len(used)==len(events) and len(used)<48,
                    'valid_attempts':sum(next(r for r in rs if r['id']==i)['evaluation']['valid'] for i in used)})
    # Stop gate uses training only, never reads heldout.json.
    dominance=[]
    for seed in range(100):
        group={r['method']:r for r in rows if r['seed']==seed and r['view']=='attempts'}
        t=group['response']
        dominance.append(all(group[m]['train_mean']<t['train_mean']-1e-10 and group[m]['cost_cny']<=t['cost_cny'] for m in ['performance','neutral_drift','structural']))
    everbetter=any(r['train_mean']<next(x for x in rows if x['seed']==r['seed'] and x['method']=='performance' and x['view']==r['view'])['train_mean']-1e-10 for r in rows if r['method']=='response')
    dump('training_replay.json',{'frozen_utc':stamp(),'real_attempts':len(rs),'rows':rows,
        'early_domination_fraction':statistics.mean(dominance),'early_domination_stop':statistics.mean(dominance)>=.9 and not everbetter,
        'heldout_accessed':False,'shared_bank_not_independent_runs':True})
    print(json.dumps({'replayed':len(rows),'real_attempts':len(rs),'early_domination_fraction':statistics.mean(dominance),'stop':statistics.mean(dominance)>=.9 and not everbetter}),flush=True)


def heldout():
    if (ROOT/'heldout_evaluations.json').exists():raise SystemExit('Held-out results already exposed; no repeat/tuning')
    replay_data=read('training_replay.json')
    frozen_hash=sha((ROOT/'training_replay.json').read_bytes())
    traces=read('workloads/heldout.json')
    evaluations={}
    sources={p['id']:p['source'] for p in read('parents.json')}
    sources.update({r['id']:'calls/'+r['id']+'/program.py' for r in records() if r['evaluation']['valid']})
    cache={}
    for cid,path in sources.items():
        source=(ROOT/path).read_text(encoding='utf-8');h=sha(source)
        if h not in cache:cache[h]=evaluate(source,traces)
        evaluations[cid]=cache[h]
    dump('heldout_evaluations.json',{'started_after_selection_hash':frozen_hash,'evaluations':evaluations,'unique_sources':len(cache)})
    rows=[]
    for r in replay_data['rows']:
        ev=evaluations[r['best_id']]
        rows.append({**r,'heldout_mean':ev.get('mean'),'heldout_valid':ev['valid'],
            'hindsight_heldout_best':min([evaluations[i].get('mean',1e6) for i in list(sources)[:8]+r['events'] if i in evaluations])})
    summary=[]
    for view in ['attempts','priced']:
        for method in METHODS:
            sub=[r for r in rows if r['method']==method and r['view']==view]
            summary.append({'view':view,'method':method,'mean_heldout':statistics.mean(r['heldout_mean'] for r in sub if r['heldout_mean'] is not None),
                'mean_train':statistics.mean(r['train_mean'] for r in sub),'mean_attempts':statistics.mean(r['attempts'] for r in sub),
                'mean_cost_cny':statistics.mean(r['cost_cny'] for r in sub),'pool_exhaustion_fraction':statistics.mean(r['pool_exhausted'] for r in sub),
                'mean_eval_seconds':statistics.mean(r['evaluation_seconds'] for r in sub)})
    dump('comparison.json',{'selection_sha256':frozen_hash,'summary':summary,'rows':rows,
        'warning':'100 correlated allocation replays of one measured bank, not 100 independent LLM trials'})
    print(json.dumps(summary,indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['prepare','acquire','replay','heldout']);parser.add_argument('--stage')
    a=parser.parse_args()
    if a.command=='prepare':prepare()
    elif a.command=='acquire':acquire(a.stage)
    elif a.command=='replay':replay()
    else:heldout()


if __name__=='__main__':main()
