# Frozen real-LLM edit pilot — 20 October 2026

This extends, and does not replace, the two negative CPU pilots. No authentic
generated parent/offspring archive was located in the already inspected pinned
MetaMuse repository or official supplement. The nine supplement records are
human cache baselines. The public-archive search in the previous audit is reused.

## Question and scope

Can edit responses improve a retention decision beyond current performance,
neutral replacement, structural diversity, or ordinary offspring quality after
charging probes? This is a one-decision refinement screen, not a reproduction
of full MetaMuse or an adaptive multi-generation search.

Eight executable human seed implementations form four semantically equivalent
pairs: best fit, first fit, worst fit, and target-residual fit. Equivalent
implementations deliberately differ in arithmetic representation. This limits
generalization; it does not by itself establish an interesting phenomenon.
No grammar mutation generates the children: every child must come from the API.
The real task is online bin packing, capacity 100. A pure Python scalar scorer
is evaluated for every feasible bin, maximizing score and breaking ties by ID.
A new bin is forced only if none fits. Stateless scorers are a narrower search
space than the original MetaMuse interface; this restriction applies to all arms.

## Workloads and separation

Use the previous four workload families and generation rules, with fresh seeds
20261040 (training) and 20261041 (shifted test), 12 traces per split, 192 items
per trace. Metric: mean 100*(bin count-volume lower bound)/volume lower bound.
Do not alter these workloads after observing outputs. No workload items, test
scores, or feedback from later children enter prompts. Selection sees training
scores only. Held-out evaluation is a separate final command after the complete
selection replay and its hashes have been saved.

## Acquisition and execution

GLM-4.7 via the documented BigModel standard OpenAI-compatible API, using the
existing ANTHROPIC_AUTH_TOKEN in memory only. No credential files are written.
The standard endpoint is chosen so that token pricing and subscription-tool
restrictions do not get conflated. An incompatible key is a stop condition;
no switch to a subscription endpoint to bypass it.

At most 112 total attempts: 8 parents * (2 probe edits + 12 independent future
edits). Two labels: local scoring refinement and alternative scoring design.
Both labels are shared across parents and policies. Each probe uses one label;
future requests use six per label. Randomize order within each stage. No retries.
Do not infer different stochastic kernels from two differing sampled children.

Calibration: first 4 scheduled probe attempts, then the other 12 only if the
route, usage accounting and scorer parsing work. Require >=3/4 valid. After 16
probe attempts require >=12/16 valid and at least two distinct useful children
(training improvement over their own parent), or stop for lack of decision value.
Main future acquisition is 3 rounds of 32 attempts. Before another round,
using training only, stop if response selection is strictly dominated by all
three performance-only/neutral/structural controls in both current training
incumbent and paid cost for >=90% of replay seeds and is never better. Do not
inspect test scores for stopping or revise the mechanism within this paid run.

Generated code is never passed to Python exec/eval/compile. A purpose-built
AST interpreter supports scalar assignments, conditions, returns, bounded
arithmetic and a few whitelisted numeric functions. No imports, attributes,
loops, recursion, collections, objects, file/network access, or access to host
globals. Limit source size, AST size, operations and numeric magnitude. Reject
invalid output; retain it with its cost. All requests, raw responses, extracted
source, evaluations and failures receive IDs and hashes.

## Budget

Verified official pricing saved under sources/: GLM-4.7 <32k input and >=200
output: CNY 3/M input, CNY 14/M output; higher tier CNY 4/16. Charge the higher
4/16 rates conservatively, ignore cache discounts. Hard output limit 1200
tokens, ASCII prompt <=6000 bytes, conservative input reservation 8192 tokens.
Per-attempt reserve: CNY .051968; total 112: CNY 5.820416. Treat 1 CNY as
1 USD for a deliberately overconservative dollar-equivalent ceiling. This is
not a currency quotation. Stop if reported usage exceeds the reservation.
Attempts without usage are charged their full reserve. All failed HTTP calls
count toward the attempt cap. Maximum request wall time 90s; no SDK retries,
redirects, tools, training, GPU, balance query or credit purchase.

## Retention comparisons

All selectors get the same eight initial candidates and retain four parents.
All generated children, including paid probes, can become the final output;
the output is the training-best observed candidate, with ID tie-break. The
test metric of that output is the primary endpoint. Also report the hindsight
best held-out candidate only as a separate diagnostic.

1. Performance only: four lowest current training means, source-ID tie-break.
2. Random: four uniformly chosen seeds.
3. Neutral drift: process seeds in a seeded common permutation, replace exact
   training-vector duplicates with the latest representative, then keep the
   four best remaining cells (fill remaining places from latest seeds).
4. Structural: protect training best and greedily maximize minimum normalized
   AST node-histogram distance.
5. Response: same retention rule on concatenated signed per-trace responses
   to the two probe labels. Invalid child uses a fixed +100-point penalty.
6. Cost-matched probing control: obtain the same sixteen probes, ignore their
   responses for parent retention, use performance-only retention.
7. Offspring quality: pay the same probes, retain four by probe mean quality.

Probe arms pay sixteen calls/evaluations before future proposals; cheap arms
spend this budget on ordinary edits. A shared offline bank gives independent
future edits to the selected parents in round-robin order, with seeded order
within each parent's future samples. Replays are allocation decisions on the
same bank, NOT independent LLM experiments. Record 100 seeded replays to expose
allocation sensitivity; do not turn them into independent-sample significance.

Compare at 48 total attempt/evaluation credits and also at a shared realized
token-price budget. The latter budget is fixed after the four-call calibration
as 32 times mean observed calibration price (pricing calibration, not policy
tuning). Use the last completed request prefix within that cost; explicitly
report unused budget, request-boundary granularity and pool exhaustion. No
claim of exact monetary matching if the finite pool cannot reach the budget.
Report cost curves, actual token costs, validity, useful children, duplicates,
wall times and evaluations. CPU time is measured separately, not silently
converted to an arbitrary dollar price. Distinguish equal evaluation credits
from equal CPU seconds.

## Interpretation

Independent future children, unavailable at selection, test whether probes
predict future training improvement. Per-parent and within-equivalent-pair
effects are descriptive with only eight parents. No kernel estimation claim.
PROMISING METHOD requires an advantage over all strong controls on held-out
quality under both accounting views, without failures, pool exhaustion or
leakage explaining it; even then larger replication is needed. Otherwise:
INTERESTING PHENOMENON, NEGATIVE RESULT if cheap controls dominate, or INCONCLUSIVE
for insufficient validity/control/power/infrastructure. No additional paid
round, email, repository modification, commit or push is authorized by this run.
