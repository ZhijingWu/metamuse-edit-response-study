"""Reconstruct the complete balanced comparison without writes or API calls."""
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('pilot',ROOT/'llm_pilot.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
allowed={r['id'] for r in m.read('schedule.json')[:48]}
all_records=m.records()
balanced=[r for r in all_records if r['id'] in allowed]
assert len(balanced)==48
m.records=lambda:balanced
captured={}
m.dump=lambda path,obj:captured.update({path:obj})
m.replay()
actual=captured['training_replay.json']
expected=m.read('training_replay.json')
assert actual['rows']==expected['rows']
assert actual['real_attempts']==expected['real_attempts']==48
comparison=m.read('comparison.json')
test=m.read('heldout_evaluations.json')['evaluations']
assert all(row['heldout_mean']==test[row['best_id']]['mean'] for row in comparison['rows'])
print(json.dumps({'balanced_bank_attempts':48,'reproduced_rows':len(actual['rows']),
    'all_selection_and_cost_rows_identical':True,'heldout_lookup_identical':True,
    'paid_calls':0,'files_written':0}))
