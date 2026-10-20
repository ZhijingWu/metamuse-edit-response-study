# Frozen targeted continuation — 20 October 2026

Scope: compare retention information, not create a new bin-packing heuristic.
All prior pilot files and manifests remain immutable. This independent adapter
is not an official MetaMuse reproduction and asserts no performance-equivalence
bug in MetaMuse. The previous result remains INCONCLUSIVE for its original
endpoint. This protocol is frozen before any new model requests or new test
evaluation. Mechanism revisions have seen the earlier results; validation must
therefore use fresh descendants AND a genuinely new held-out workload set.

## Design diagnosis and economy

The old bank contains 16 probes, 43 completed future responses and one failed
future transport attempt. To fill its original 12-future-slots-per-parent matrix
would require 52 previously unattempted requests; 53 would also replace the
failed slot, with the failure still charged. Completing it would cure pool
censoring but would reuse future outcomes already seen while revising selectors.
It is not the primary validation chosen here. No missing old outcomes are filled
with estimates or fabricated programs.

A fully prospective online comparison of twelve policies would repeat shared
requests and use substantially more budget. Instead, reuse the 16 old probes,
charge their measured original acquisition/evaluation costs to every policy
that accesses them, and acquire a common matrix of independent fresh future
edits. Old future children, including the known winner, are excluded from
generation, initial incumbents and selection. Their results cannot manufacture
an advantage for the revised policy.

The target horizon is 32 paid API-attempt/evaluation credits. With eight possible
parents, four retained parents and zero-probe controls, complete support requires
eight future samples per possible parent: 8*(32/4)=64 logical requests. Probe
arms spend 16 credits on old probes and can spend 16 on fresh edits; the local-
only arm spends eight and can spend 24 on fresh edits. This is smaller than a
fresh 48-credit matrix (96 future requests), while testing the horizon at which
the earlier result was confounded by cheap-arm pool exhaustion. No expansion
to 48 credits is part of this continuation.

The common-pool design supports a conditional one-retention-step comparison;
it does not establish multi-generation or across-task method superiority.
Allocation replays integrate choices on one measured matrix. They are not
independent LLM experiments. Equal budgets mean common resource ceilings,
not a claim that every discrete request prefix spends exactly the same amount.

## Fixed task, source and model

Reuse the eight human parent source files and 12 training traces exactly from
../metamuse_llm_pilot/. Reuse its pure scalar AST interpreter, packing semantics,
source extractor, system prompt, local/alternative edit prompts and API payload:
glm-4.7, standard https://open.bigmodel.cn/api/paas/v4/chat/completions,
temperature 0.9, thinking disabled, stream false, max_tokens 1200.
The provider alias is not an immutable model revision. No history, old winner,
training outcomes, old test scores or new test items enter the model context.

Generate eight new future edits per parent, four per edit label. Randomize
request order within each pair of slots (16 requests), with frozen seeds
20261071 through 20261074. Every new response is logged, including invalidity,
duplicate behavior, usage and failures. Old generated programs are not treated
as new requests. No grammar edits substitute for real model outputs.

## Fixed selectors

Protect the best current performer for farthest-point selection. Use the old
quality/ID tie-break rules. Archive size is four. Selectors see only parent and
old probe training data; fresh descendant outcomes do not revise retention.

1. performance: lowest current means, ID ties (original comparator).
2. random: uniformly select four of eight parents.
3. neutral: one uniformly chosen representative per exact training-bin vector.
4. performance_cells_short: one shortest canonical source per training-vector
   cell, then keep the four best cells. This is ordinary cheap retention,
   motivated by existing program-database practice, not a new mechanism.
5. structural: original normalized AST node-type histogram diversity.
6. response_current: original two-label signed training responses, invalid
   child = parent +100 percentage points, farthest-point retention.
7. response_masked: same signed valid responses; pairwise distance averages only
   coordinates of labels for which both probes are valid. No jointly observed
   label gives distance zero. Invalidity itself has no diversity reward.
8. response_complete: require both probes valid to be eligible for retention;
   then use ordinary response distance. There are seven eligible old parents.
9. response_local: use the preselected local-edit probe only (eight paid probes),
   with invalid responses masked as above. This is a cost ablation, selected
   after old results, not a validated novel acquisition algorithm.
10. offspring_quality: original two-probe mean, invalid penalty +100 points.
11. probe_control: same sixteen probes but performance-only parent retention.
12. validity_only: diversity of the two validity flags; this explicitly tests
    whether the apparent benefit can be reproduced by failure identity alone.

The penalty sweep 0,1,10,100,1000 and complete/masked/local diagnostic was
specified and saved from parent/probe training data before acquisition. Do not
choose a winning penalty using the new test set. The primary revised descriptor
is response_masked, with response_complete as robustness and response_local as
the cheaper acquisition ablation. All twelve selectors must be reported.

## Costs and stopping

Additional authorization: <=128 attempts and <=CNY10. Operational hard ceiling:
64 logical requests plus at most ONE transport retry across the entire run,
so <=65 attempts. No parse/numerical failure is retried. If a transport error
occurs, log and charge its full reserve, wait 10 seconds, then retry that logical
request once if the single retry remains. A second transport failure anywhere,
HTTP error, absent usage, wrong returned model, token-cap violation or first-
eight validity below 6/8 stops acquisition. There is no endpoint fallback.
This explicitly budgets the sole allowed retry; it is not an unlimited SDK loop.

Each attempt reserves 8192 input and 1200 output tokens at the higher verified
GLM-4.7 rates CNY4/M and CNY16/M: CNY0.051968. Full ceiling CNY3.37792 < CNY10.
Observed prior average predicts roughly CNY0.16 nominal / CNY0.25 conservative,
including one failed-call reserve. Reverified official pricing is saved under
sources/pricing.md. No balance query, credential change, credit purchase,
training, GPU rental or new provider. Credentials stay in process memory only.

First eight logical requests are the compatibility/validity screen, counted
in the same matrix. If they pass, finish the fixed 64-request matrix unless a
listed failure stop fires. Intermediate cheap wins at a shorter horizon are
not grounds for claiming a result at 32 credits; the matrix is the minimum
support for that endpoint. No second paid matrix or tuning round is automatic.

## Replay and fresh evaluation

Use 560 seeded allocation draws solely as numerical integration on the measured
matrix: 70 random parent sets each occur eight times; 16 neutral-representative
sets each occur 35 times. Fresh children are independently ordered within each
edit label, then interleaved, so two/four/six/eight future draws preserve label
balance when no failure/budget boundary interrupts. The same ordering is shared
by all methods. No confidence interval treats these 560 draws as LLM repeats.
Log every event and aggregate all probes, failed attempts, retries, tokens,
request times and evaluation times. The training-best observed valid program
is the output; code ID resolves ties. Probe children are eligible outputs.

Report curves at 8,16,24,32 credits, and two 32-credit endpoints:
(a) 32 API attempts and <=32 training-evaluation credits;
(b) the same plus a CNY0.062416 nominal-price ceiling and 30-second measured
training-evaluation-time ceiling. The money ceiling is 32 times the old four-
call calibration's tier-aware price, fixed without new outcomes. Initial eight
seed evaluations and selector computation are common/recorded overhead. Count
the old probe costs where accessed; no probe becomes free because it is reused.
The output after the last affordable complete event is scored; unused budget
and event-boundary granularity are reported. Failure/retry events count as
separate paid attempts. Any unavailable outcome is censored, never imputed.

Before computing any new test scores, save selections, event prefixes and their
hashes. The new test is eight independently seeded shifted workload banks,
20261110 through 20261117, each containing the same four families * three traces
and 192 items per trace: 96 fresh traces. No old training/test item sequence may
be identical to a new sequence. The mechanism is fixed before writing these
test workloads; generation/selection never reads them. Evaluate after acquisition
ends. A test-invalid chosen program is reported as failure, not silently removed;
use worst feasible packing cost only as an explicitly labeled conservative
summary and do not claim superiority if validity explains it.

Use paired per-workload-bank comparisons to describe workload sampling
uncertainty separately from the fixed descendant matrix. Eight workload banks
are not eight independent LLM searches. Report conditional effects and sensitivity
to the finite eight-parent bank. Old winner can be scored afterward as a labeled
reference, never as a selector input or an excluded unfavorable result.

## Decision

An advantage must survive the cheap cell/short-code, random, neutral, structural,
offspring-quality and probing controls under both cost views; a win caused only
by invalidity magnitude is not useful response evidence. More sampled child
diversity or a single good child does not justify a new selection mechanism.
Accept cheap-control dominance. If results are flat, do not buy more samples
automatically. Even a positive conditional result requires independent parent-
bank validation before a novelty claim. No email or Technical Note is produced.
