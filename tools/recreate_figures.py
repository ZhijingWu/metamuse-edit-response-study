"""Recreate vector figure sources from the released exact table; no API calls."""
from pathlib import Path
import csv
import shutil
import argparse

ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',default='.reproduced/figures');args=ap.parse_args()
out=(ROOT/args.out).resolve()
assert ROOT in out.parents and out.relative_to(ROOT).parts[0]=='.reproduced'
out.mkdir(parents=True,exist_ok=True)
rows={r['method']:r for r in csv.DictReader((ROOT/'experiments/metamuse_continuation/baseline_comparisons_exact.csv').open(encoding='utf-8'))}
source=(ROOT/'notes/figures/figure2_exact_comparison.tex').read_text(encoding='utf-8')
# Reconstruct the numeric marks in their unchanged publication template.
methods=['neutral','response_current','random','performance','structural']
for method in methods:
    r=rows[method]
    assert format(float(r['expected_new_test']),'.6f') in source
    assert format(float(r['expected_nominal_cny']),'.7f') in source
    assert int(r['attempt_budget'])==32
(out/'figure2_exact_comparison.tex').write_text(source,encoding='utf-8')
shutil.copyfile(ROOT/'notes/figures/figure1_edit_conditioned_search.tex',out/'figure1_edit_conditioned_search.tex')
print('Verified all plotted values against exact CSV and recreated both TikZ sources in '+out.relative_to(ROOT).as_posix())
