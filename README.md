# When Performance-Equivalent Programs Differ Under Edits

**A Controlled Study of Search Representation and Retention**  
Zhijing Wu — Sichuan University

Independent exploratory study motivated by [MetaMuse, ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/85632be2cd69e9a0ef4ba054c096fac9-Abstract-Conference.html).
This is **not an official reproduction**. No new algorithmic superiority was established.

**[Read the two-page Technical Note](notes/Zhijing_Wu_MetaMuse_Search_Representation_Note.pdf)** · [LaTeX source](notes/Zhijing_Wu_MetaMuse_Search_Representation_Note.tex) · [Reproducibility](docs/REPRODUCIBILITY.md) · [Claims and evidence](docs/CLAIMS.md)

## Research question

Can edit-conditioned information improve actual algorithm discovery at matched total search cost beyond neutral retention, random retention and ordinary performance selection?

MetaMuse explores algorithmic diversity through measured workload performance, external stimuli and waypoint reasoning. Equal measured costs on observed workloads need not imply equal behavior under later edits. But a response difference alone does not establish predictive usefulness, and useful information must repay its acquisition cost. This study tests those distinctions in a restricted online bin-packing interface; it does not identify a performance-equivalence bug in MetaMuse.

## Experiments and findings

| Stage | Evidence | Conclusion |
|---|---|---|
| CPU finite grammar | 625 coefficient policies; 5,628/5,655 same-performance pairs (99.52%) have different uniform one-step mutation-response distributions | Exact finite-grammar phenomenon; two response selectors fail to beat strong cheap controls |
| Initial real-LLM pilot | 60 attempts, 59 responses, 58 executable; modest candidate improvement on the original 12-trace test | **INCONCLUSIVE** for the originally planned full comparison; acquisition was interrupted |
| Targeted continuation | 64 fresh requests, 64 responses, 58 executable; complete 32-credit comparison and 96 fresh held-out traces | **NEGATIVE for the tested response-aware selectors** |

The completed primary endpoint integrates label-balanced future subsets and retention choices on **one recorded parent/offspring matrix**. Allocation replays are not independent LLM experiments.

| Retention policy | Charged probes within 32 attempts | Expected held-out cost ↓ | Expected nominal CNY |
|---|---:|---:|---:|
| Neutral | 0 | 6.793448 | 0.0546779 |
| Current response diversity | 16 | 6.793448 | 0.0577888 |
| Random | 0 | 6.793599 | 0.0546779 |
| Performance only | 0 | 6.793752 | 0.0572926 |
| Structural | 0 | 6.793143 | 0.0538330 |

Response retention ties neutral while costing **5.69% more** in estimated generation spending. Shorter-representative retention also scores 6.793143; the tiny ranking difference does not establish overall structural superiority. Masking invalid responses and other controls do not demonstrate a response-information advantage. [All twelve selectors and exact values](experiments/metamuse_continuation/baseline_comparisons_exact.csv) are retained.

An artificial invalid-child penalty supplies **99.945%** of the squared distance responsible for the first diverse choice. This explains that retention decision, not every observed response difference. The earlier candidate's average held-out improvement did not repeat on the fresh traces.

Cost is mean `100 × (bins − ceil(total item volume / capacity)) / ceil(total item volume / capacity)` over traces. Differences are percentage points, not percentage reductions in bin count. Generation prices are historical token-price estimates, not account invoices. Equal budget ceilings permit different realized spending.

## Offline reproduction

Python 3.10+; standard library only. Run from the repository root:

```sh
python -m pip install --no-index -r requirements.txt
python -B tools/reproduce.py verify
python -B tools/reproduce.py all --out .reproduced/check
python -B tools/recreate_figures.py
```

The replay process disables network connections, writes only below `.reproduced/`, reconstructs both CPU selection comparisons, verifies the complete balanced subset of the interrupted pilot, recalculates all twelve exact continuation rows and the additional cost curves, and checks the scalar evaluator against existing seed outcomes. It creates no new candidates and sends **zero API requests**. See [tested commands and limits](docs/REPRODUCIBILITY.md).

## Artifact layout

- `experiments/metamuse_pilot/`: finite grammar, both CPU banks, original/corrected negative comparisons, configurations and histories.
- `experiments/metamuse_llm_pilot/`: restricted AST evaluator, generation/selection code, human seeds, frozen synthetic splits, sanitized prompts, generated text/programs, results and interrupted accounting.
- `experiments/metamuse_continuation/`: protocol/freezes, fresh candidate matrix, all selectors, trace-level evaluations and exact comparisons. The large replay JSON is losslessly compressed once.
- `tools/`: tested offline entry points; `notes/`: final PDF, LaTeX and vector figure sources.
- `docs/`: reproduction, claims, licensing/publication audit and six historical research reports.
- `provenance/`: original development-manifest identities and the sanitized-export map. `ARTIFACT_MANIFEST.json` verifies the public release itself.

Provider response envelopes and request IDs, downloaded third-party papers/documentation, local application materials, caches and redundant derived copies are excluded. Sanitized records preserve generation content, conditions, scientific outcomes, failures and costs. [Publication scope](docs/LICENSING_AND_PUBLICATION.md) distinguishes original material from model-generated records.

## Limits

One parent bank; four elementary heuristic families; a stateless scalar interface; two reused probe samples per parent; and a provider alias (GLM-4.7) without an immutable revision or provider seed. Neutral retention is a one-boundary analogue of drift. The eight test banks describe workload variation, not independent model searches. These results neither prove a universal impossibility nor reproduce full MetaMuse or cited evolutionary systems. New stochastic API calls cannot be promised to regenerate the recorded programs.

The open question remains when edit-conditioned information can justify its acquisition cost. These results support no new selection algorithm and no further tuning on the exposed test traces. Paid acquisition is separate historical code, excluded from every reproduction command; see [acquisition documentation](docs/PAID_ACQUISITION.md).
