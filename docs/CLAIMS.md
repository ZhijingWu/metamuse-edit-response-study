# Claims and frozen evidence

The two-page note is an independent undergraduate exploration motivated by MetaMuse. It is not an accepted-paper claim, official reproduction, new selection algorithm or finding of a MetaMuse bug.

| Claim | Public evidence |
|---|---|
| 625 CPU programs; 5,628/5,655 same-performance pairs = 99.52% | `experiments/metamuse_pilot/results/landscape.json`, `config.json`, `pilot.py` |
| Both CPU selectors fail against cheap strong controls | First `results/runs.csv`, corrected `selective_results_corrected/runs.csv`; superseded results retained separately |
| Initial run remains incomplete/inconclusive: 60/59/58 | `experiments/metamuse_llm_pilot/accounting_final.json`, `EXECUTION_STOP.md`, `FINAL_DECISION.json` |
| Initial candidate test 7.261433243575846 → 6.988209199859999 on 12 traces | Initial pilot `candidate_improvement.json`; two trace wins, ten ties; no completed method-superiority claim |
| Fresh continuation 64/64/58; no retry | `experiments/metamuse_continuation/ledger.json`, per-call results |
| Current response and neutral both round to 6.793448 at 32 credits | Continuation `baseline_comparisons_exact.csv`, `exact_training_selection.json`, `exact_conditional_comparison.json` |
| Response expected money +5.69% | `(0.0577888 / 0.0546779 - 1) × 100 = 5.6895016085109384%`; historical nominal token prices, not an invoice |
| Structural and shorter representatives 6.793143 | Same exact CSV; tiny differences do not establish overall superiority |
| Invalid coordinate contributes 99.945% of the key squared distance | `interpretation_checks.json`, `descriptor_diagnosis.json` |
| Fresh 96 traces, eight workload banks, no original sequence duplicate | `workloads/new_heldout.json`, `config.json`, freeze/verification records |
| Old winner's improvement does not repeat | `interpretation_checks.json`: 6.800138 vs Best Fit 6.793143, 1 win / 94 ties / 1 loss |

All twelve selectors are reported. Exact/numerical allocation integration concerns one recorded model-search matrix; neither 100 nor 560 allocations are independent LLM trials. Workload-bank uncertainty is distinct from independent-search uncertainty. The retained metric is percentage excess over the volume lower bound, with differences in percentage points.

Historical reports in `docs/reports/` document stage-specific decisions; an earlier statement that no note had been produced describes that earlier stage, not the current release. Development manifests and freeze hashes refer to original bytes. The export map identifies sanitization, and the public manifest verifies released bytes. Provider envelopes and local correspondence are not asserted to be public.
