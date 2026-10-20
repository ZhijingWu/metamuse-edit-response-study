"""One non-paid calibration parser repair, with original records preserved."""
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('pilot',ROOT/'llm_pilot.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
assert len(m.attempts())==4 and not (ROOT/'PARSER_REVISION.json').exists()
changed=[]
for r in m.records():
    directory='calls/'+r['id']
    old=r['evaluation']
    try:
        source=m.extract_source((ROOT/directory/'content.txt').read_text(encoding='utf-8'))
        (ROOT/directory/'program.py').write_text(source,encoding='utf-8')
        r['program_sha256']=m.sha(source)
        r['evaluation']=m.evaluate(source,m.read('workloads/train.json'))
    except Exception as e:
        r['evaluation']={'valid':False,'reason':type(e).__name__+': '+str(e)[:160]}
    r['parser_revision']=2
    m.dump(directory+'/result.json',r)
    changed.append({'id':r['id'],'old_valid':old['valid'],'new_valid':r['evaluation']['valid']})
cfg=m.read('config.json');oldsha=cfg['script_sha256']
cfg['script_sha256']=m.sha((ROOT/'llm_pilot.py').read_bytes())
cfg['parser_revision']=2
m.dump('config.json',cfg)
m.dump('PARSER_REVISION.json',{'utc':m.stamp(),'before_script_sha256':oldsha,
    'after_script_sha256':cfg['script_sha256'],'records':changed,'paid_calls':0,
    'reason':'Extract a unique fenced Python block even when prose precedes it; permit bounded numeric bases up to the existing 1e12 magnitude limit in power expressions. Exponents remain capped at 4. All original records/config/script preserved in pre_parser_fix and result_parser_v1.json. No policy or workload change.'})
rs=m.records();ledger=m.read('ledger.json');ledger['valid_programs']=sum(r['evaluation']['valid'] for r in rs)
m.dump('ledger.json',ledger)
cal=m.read('calibration.json');cal['valid']=ledger['valid_programs'];cal['parser_revision']=2
m.dump('calibration.json',cal)
print(changed)
