# Initial real-LLM pilot — INCONCLUSIVE

The run completed 60 attempts, 59 API responses and 58 executable candidates, then stopped after a transport failure with zero retries. Its originally planned full-budget comparison is incomplete. Protocol, configuration, parser/futility freezes, output text, extracted programs, synthetic workloads, evaluations and ledgers retain the evidence.

`calls/<id>/request.json` retains prompts and generation conditions without authorization headers. `content.txt` retains model text; `program.py` retains extracted code when available. `result.json` retains scientific outcomes, usage and costs with provider response IDs removed. Full provider response envelopes, parser-code backups, redundant snapshots and downloaded provider documentation are intentionally omitted. The export map and development manifest record their identities; sanitized files do not pretend to retain original byte hashes.

From the repository root run `python -B tools/reproduce.py initial`. This reconstructs the complete balanced 48-attempt subset without writes or API requests. It does not relabel the interrupted endpoint as complete. [Portable instructions](../../docs/REPRODUCIBILITY.md) supersede commands referring to the original local workspace. Historical acquisition is separate and is never a reproduction step.

The evaluator in `llm_pilot.py` interprets a closed scalar AST; generated source is not executed as arbitrary Python. Model-generated records are identified and excluded from the root MIT grant; see the [publication audit](../../docs/LICENSING_AND_PUBLICATION.md).
