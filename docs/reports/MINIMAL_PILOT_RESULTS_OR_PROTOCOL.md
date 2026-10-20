# Minimal pilots: results and next protocol

**Actual results, not a proposed-only study.** Two bounded CPU pilots tested generated bin-packing programs and changed search behavior. Neither established a worthwhile improvement over the strongest cheap controls. No LLM, embedding model, paid service, GPU or downloaded workload dataset was used. Assessment: **20 October 2026**.

## Reproduction and preserved artifacts

All code/configuration/raw data are under `experiments/metamuse_pilot/`. Run from the existing workspace:

```powershell
python -I -B work/metamuse_pilot/pilot.py
python -I -B work/metamuse_pilot/sensitivity.py
python -B work/metamuse_pilot/behavior_audit.py
python -B work/metamuse_pilot/selective_pilot.py
```

Artifacts: `config.json`, `selective_config.json`, the four scripts, generated workload JSONs, full program-bank score matrices, per-run and per-attempt CSVs, summaries and SHA-256 manifests. `FINAL_MANIFEST.json` identifies retained versus superseded results. Configurations were locally frozen before their corresponding outcomes, not publicly preregistered. The sensitivity/behavior checks and second mechanism were developed after the first result and are explicitly exploratory.

The current upstream repository and supplement were not modified. Only reviewed standalone `Bin`/`BPPEval` class definitions were extracted for conformance; the full package, pickle loader, model client and arbitrary generated source were not executed.

## Task and generated programs

Enumerate **625 deterministic programs**, four coefficients in `{-2,-1,0,1,2}`. For each feasible existing bin, choose the minimum of

`a·r + b·r² + c·(bin_index+1)/(num_bins+1) + d·1[r<0.2]`,

where r is residual capacity after placement divided by 100. Break ties by bin index. Open a bin when none fits. These are **grammar-generated programs, not LLM-generated discoveries**. The restricted family intentionally makes complete neighborhood analysis affordable; no novel bin-packing heuristic is claimed.

Use 12 training and 12 held-out shifted workloads per bank, 96 positive integer items per workload, capacity 100. Families: uniform, Weibull, complementary sizes and phased small/large items. Shift distribution parameters or phase order for testing. These are newly generated public reproducible workloads, not the paper's exact benchmark selection.

The objective matches the inspected BPP evaluator: mean percentage excess over each trace's lower bound, `100 × (bins−l1_bound)/l1_bound`; **lower is better**. It is not the paper's headline reduction relative to First Fit. Forty-eight native-core/mirror checks agreed; every simulated packing also checked capacity and item conservation. This establishes limited evaluator conformance, not full upstream reproduction.

## Pilot 1: does current performance preserve mutation behavior?

Frozen train/test seeds: `20261020` / `20261021`. Eight labeled edits change one coefficient by ±1 with wraparound. Exact training score vectors define the current cells. Compute the uniform edit-transition distribution over destination performance cells.

| Exhaustive result | Value |
|---|---:|
| Programs / current-performance cells | 625 / 172 |
| Non-singleton cells | 82 |
| Same-performance program pairs | 5,655 |
| Pairs with different next-cell distributions | 5,628 (**99.52%**) |
| Maximum total-variation distance | 1.0 |

This is an exact finite-bank count, not a population estimate about LLM programs. Some obvious witnesses differ only by positive coefficient scaling, so they cannot carry a novelty claim.

**Exploratory robustness checks:** without wraparound, 5,585/5,655 aliased pairs differ. After positive-scaling canonicalization, 3,977/4,019 pairs differ under no-wrap edits (**98.95%**); sign-flip edits give 3,707/4,019 (**92.24%**). Full training action sequences yield 385 cells: 1,504/1,518 pairs with identical executed action sequences still have different no-wrap next-performance kernels (**99.08%**). These stronger checks reduce two simple explanations, but still concern a restricted grammar and finite workload suite. The general phenomenon is consistent with established neutral-drift/evolvability research.

### Search intervention, with probe cost charged

Each run has an archive of eight, eight common initial programs and **120 attempted candidate evaluations**, including repeated/probe requests. Thirty seeds vary initial pools and proposal choices; they are not 30 independent workload samples. Precomputed tables are masked: the selector only receives scores it requests. Test scores never enter selection. The table computation is experimental setup, not free real-world algorithm evaluation.

The response method uses two labeled child responses as its diversity descriptor. All probe-based controls pay the same two probes per primary candidate. Flat controls instead spend the whole budget on ordinary proposals. Probe children count toward best-so-far output but, in this simplified protocol, only primary candidates become active parents. That restriction is shared by all probe-based arms and is a limitation relative to a fully general search system.

| Method | Mean training cost | Mean held-out cost |
|---|---:|---:|
| Fitness-only, no probes | 12.40826 | 8.51877 |
| Performance diversity, no probes | 12.40284 | 8.55706 |
| Independent random search, no probes | **12.38507** | **8.49605** |
| Performance diversity, same probes | 12.39666 | 8.50741 |
| Structural coefficient diversity, same probes | **12.38507** | **8.49605** |
| **Edit-response diversity, same probes** | **12.38507** | **8.49605** |
| Offspring mean/variance descriptor | 12.41443 | 8.53918 |
| Best observed offspring-quality selection | 12.40826 | 8.51877 |
| Reservoir retention, same probes | 12.39666 | 8.50741 |

The response method tied random search and structural diversity in all 30 final-budget comparisons. This does not reproduce MetaMuse, MAP-Elites, Quality Evolvability ES or Clade-AHD; the controls isolate analogous information/selection principles in the common finite search.

There is a ceiling: **35/625 programs attain the bank's minimum training cost**. Random search reaches the same final result easily. The response method is not superior on the stored intermediate curves either in a consistent sense; do not mine an early favorable checkpoint as a new positive result.

## Pilot 2: probe only at performance collisions

After the first negative result, freeze a fresh train/test bank (`20261022` / `20261023`) and the collision-triggered rule specified in the design report. Compare 30 paired seeds, the same 120-request budget and common initial pools. Every matched pair of two edits costs four probes. All evaluated probe children remain eligible as final outputs.

Headline results use `selective_results_corrected/`:

| Method | Mean training cost | Mean held-out cost | Mean probe attempts |
|---|---:|---:|---:|
| Performance-diversity archive | 11.75750 | 8.71223 | 0 |
| **Collision-triggered response refinement** | 11.74026 | 8.69415 | **63.07** |
| Same collision probes, coin-flip retention | 11.74604 | 8.72962 | 62.13 |
| Cheap neutral drift | **11.72301** | **8.62817** | 0 |
| Independent random search | **11.72301** | 8.63775 | 0 |

The response rule is worse than neutral drift by **0.06597 percentage points** on mean test cost and worse than random by **0.05639 points**. Against neutral drift it wins/ties/loses on 3/21/6 paired seeds. Against performance diversity it wins/ties/loses on 4/20/6 despite a slightly better mean. These small, mostly tied differences are descriptive; no statistical superiority claim is made.

One implementation correction was made before adopting results: revisiting an already active program could shrink the neutral-drift archive. The pre-fix script/results are retained under `selective_results/`; the corrected run asserts archive size and is the only headline revision. The displayed summary values happened to remain unchanged after the fix. No parameter was tuned to improve treatment performance.

## Resources and interpretation

The first main run took **45.44 s**; the corrected second run took **45.79 s** on the recorded local Python/Windows environment. Each bank required 15,000 actual candidate–trace evaluations. The extra full-action audit used 7,500. Forty-eight paired conformance cases and the superseded revision are separately retained. Search replay charged 32,400 and 18,000 candidate-evaluation requests respectively; **these are cached-table simulations of search, not that many fresh executions or model calls**. Unique evaluated programs and all request roles are in the CSVs. LLM calls/tokens and API spend were **0 / 0 / US$0**. Peak memory was not measured.

Repeated requests are charged even when identical code could have been cached in a real system. This makes probe overhead explicit but limits transfer of the cost comparison. A real study must separate generation tokens, cache hits, unique executable candidates, executions, retries and wall time. The pilots cannot establish LLM sample efficiency or production generalization.

**Supported:** current outcome equivalence need not preserve a fixed edit process; two concrete policies change search trajectories; observing that distinction is not sufficient to make probes worthwhile. **Unsupported:** a new general theorem, a novel discovered packing algorithm, superiority over MetaMuse, a benefit with actual LLM mutation, or a cleared originality claim.

## Next scientifically meaningful test

Before another large search run, test **real proposal-kernel relevance**, preferably using an existing author-generated candidate/offspring archive. Match same-performing parent pairs on frozen training workloads; separate selection by current quality, structural descriptors, neutral drift, descendant-quality credit and edit-response witnesses. Hold the edit prompts/model/coder, initial pool, request order randomization and token/execution budgets fixed. Use untouched workloads and additional edit samples for the outcome. Count invalid children and duplicate outputs rather than filtering them away.

If no suitable archive exists, a screening design is **8 parent pairs × 2 parents × 2 edit prompts × 4 samples = 128 LLM edit calls**. Use source-validated existing parents or validated neutral re-expressions, rather than buying an initial generation study immediately. Set explicit token caps: at most 4,000 input and 2,000 output tokens per call gives approximately **512k input / 256k output tokens**, excluding retries. CPU evaluation needs no GPU; allow a few minutes to an hour depending on trace lengths and generated-code timeouts.

This is only a screen, not a powered estimate of high-dimensional transition distributions. Test whether a response witness predicts **useful independent descendants** better than neutral drift and structural selection. The null can hold even if empirical kernels differ. Stop if the signal vanishes, is fully explained by parameterization, or costs more than ordinary search.

Paid execution is **not authorized or recommended yet**. If this screen becomes justified, first select/verify model pricing and propose a hard cap, e.g. **US$25 including retries**, using `512k × input_price + 256k × output_price` as the base estimate. This is a proposed spending ceiling, not a current provider price quotation. No purchase, recharge or API call was made.
