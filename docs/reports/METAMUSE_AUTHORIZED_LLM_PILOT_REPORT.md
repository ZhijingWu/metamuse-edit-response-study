# Authorized MetaMuse real-LLM pilot — 20 October 2026

**Classification: INCONCLUSIVE.** The run found one genuine LLM-generated
bin-packing heuristic that improves both training and held-out quality over the
initial best seed. It did not establish a cost-matched advantage for response-aware
retention. A connection failure interrupted acquisition before the planned
comparison bank was complete. At the fully available early budget, cheap random
and neutral retention perform better than paying for response probes.

**Research decision: NO-GO for claiming a new selection method or automatically
launching another paid round.** Preserve the candidate as a small empirical
finding. No follow-up email, Technical Note, repository change, commit or push was
made. The two earlier negative CPU mechanisms remain negative; their artifacts
and the NetArena mechanism NO-GO are unchanged.

The [frozen protocol](../../experiments/metamuse_llm_pilot/PROTOCOL.md),
[configuration](../../experiments/metamuse_llm_pilot/config.json),
[complete artifact guide](../../experiments/metamuse_llm_pilot/README.md) and
[machine-readable decision](../../experiments/metamuse_llm_pilot/FINAL_DECISION.json) accompany
this report. This is an independent refinement pilot, not a MetaMuse reproduction.
The earlier [method audit](METAMUSE_METHOD_AND_CODE_ANALYSIS.md) and
[novelty map](ALGORITHM_DISCOVERY_NOVELTY_MAP.md) supply the reused source evidence.

The already inspected MetaMuse repository at
`b976a28426268e2f7310b0a8d9c33f3a82496479` and official supplement did not provide
a reusable generated parent/offspring archive; their nine archived human records
concern cache baselines. The previous public-archive search was reused rather
than repeated. This is a limitation of the inspected releases, not proof that
no archive exists elsewhere.

Eight executable human seeds form four equivalent pairs: Best Fit, First Fit,
Worst Fit and target-residual fit, expressed through different arithmetic.
All four pairs have identical training action sequences. These are elementary
human heuristics, not authentic MetaMuse creative candidates. Every proposed
child comes from a real GLM-4.7 request; no grammar mutation substitutes for it.

The shared interface generates a pure numeric bin-priority function. It can
change nonlinear arithmetic and conditions, but cannot maintain state or open
an unnecessary new bin. This is narrower than MetaMuse's original interface.
The task uses capacity 100 and 12 training plus 12 shifted held-out traces,
192 items each, across the previous uniform, Weibull, complementary and phased
families. Fresh split seeds are 20261040/20261041. Lower is better for mean
`100*(bins-volume_lower_bound)/volume_lower_bound`.

Every selector starts with the same eight seeds, retains four parents, and uses
the same two mutation instructions. The response, probing-control and
offspring-quality arms pay for two probes per seed before choosing parents.
Cheap arms use their budget for ordinary edits. All paid children can become
the training-selected final output. This tests one retention decision followed
by independent one-step children; it does not test multi-generation evolution.

All generation and retention used training information only. The complete
48-call stage supplied 16 probes and four independent future edits per parent.
Its [selection replay](../../experiments/metamuse_llm_pilot/training_replay.json) was frozen
before any test score was evaluated. Its SHA-256 is
`387171fded7bd98ac2ab02d70a881330e5f696fb6a46003d53882c7ee358e1c7`.
The additional interrupted stage remains in raw data and total accounting, but
its unequal parent coverage is excluded from the main selector comparison.
There was no further acquisition after opening the held-out results.

The strongest candidate is
[future_p06_02](../../experiments/metamuse_llm_pilot/calls/future_p06_02/program.py), an actual
local edit of the absolute target-residual seed. It was selected by training
score, not by inspecting test scores. It improves training cost from **12.8220
to 12.6897** and held-out cost from **7.2614 to 6.9882**. The test difference is
**0.2732 percentage points in the excess-bin metric**, arising from one fewer
bin on each of two Weibull traces; the other ten traces tie. This is modest,
localized evidence of useful generation, not a new bin-packing algorithm or a
state-of-the-art result. See the
[trace-level results](../../experiments/metamuse_llm_pilot/candidate_improvement.json).

The following values average 100 allocation replays of **one shared bank**.
They are not 100 independent LLM trials, and no significance claim is made.
The 16-credit column is an available common point on the declared cost curves.
The last three columns use every available event in each arm and therefore
have unequal spending. Eight identical initial seed evaluations are common
additional overhead in every arm.

| Retention policy | Held-out cost at 16 attempt credits | Held-out cost using available pool | Calls used from pool | Conservative CNY cost |
|---|---:|---:|---:|---:|
| Performance only | 7.2614 | 7.2614 | 16 | 0.04920 |
| Random | **7.1330** | 7.1330 | 16 | 0.04636 |
| Neutral replacement | 7.1576 | 7.1576 | 16 | 0.04661 |
| Structural diversity | 7.2614 | 7.2614 | 16 | 0.05061 |
| Response diversity | 7.2614 | **6.9882** | 32 | 0.09799 |
| Same probes, ignore responses | 7.2614 | 7.2614 | 32 | 0.10372 |
| Offspring quality | 7.2614 | 7.2614 | 32 | 0.10468 |

The response selector reaches the useful candidate, but its apparent later
advantage cannot be credited as method superiority: the cheap arms exhaust
their available future pools after 16 requests while the probe arms can spend
32. The planned 48-credit endpoint is unfilled. The frozen CNY 0.099616
token-price-budget view has the same censoring problem for cheap arms. Actual
execution seconds also differ. No table here asserts exact monetary and CPU
matching. The [comparison export](../../experiments/metamuse_llm_pilot/baseline_comparisons.csv)
and [complete cost curves](../../experiments/metamuse_llm_pilot/cost_curves.csv) retain
spending, request-boundary granularity, evaluation time and pool censoring.

The early result is less ambiguous: at 16 charged attempts, random and neutral
retention obtain better mean held-out quality than response probing and have
lower estimated generation cost. All probe arms are still paying their common
16-probe acquisition cost at that point. This shows an overhead problem at
that horizon; it does not prove that probes can never repay their cost later.

The four scientific questions have the following answers:

1. **Real edit-conditioned differences:** seven of eight matched parent-pair /
   instruction comparisons have different sampled probe outcomes, including
   one numerical failure. Executable child behavior varies despite equivalent
   parents. Single differing samples do not establish unequal stochastic kernels.
2. **Prediction of useful future children:** unestablished. The balanced bank
   has only two probes and four independent future samples per parent. Within
   equivalent pairs, the only comparison with nonzero probe and future useful-rate
   differences reverses direction; another probe difference disappears. Across-
   parent quality correlations are confounded by initial fitness.
3. **Effect on discovery decisions:** observed in this bank. Response retention
   preserves `p06` and reaches its useful child; performance-only retention drops
   it. Random and neutral retention also reach that child when they retain `p06`.
   The result demonstrates a consequential representation choice, not a unique
   capability of response probes.
4. **Survival against cost-matched cheap controls:** not demonstrated. Cheap
   controls win at the fully available early budget, and the full endpoint was
   interrupted. Positive candidate quality cannot fill that evidence gap.

There is a mechanism-specific caution: `p06` has one invalid probe. Encoding
invalidity as a +100-point response makes it extremely distant, so response
diversity retains it partly because of failure magnitude. Its later good child
therefore does not establish that the probe descriptor predicts productive
future edits. The source-based control is also a coarse AST histogram, and
neutral replacement is a single archive-boundary analogue of drift. No
superiority over full FunSearch, AlphaEvolve, Clade-AHD, Quality Evolvability or
MetaMuse is established. The existing novelty limitations still apply.

The run used the already configured credential in memory, with the documented
BigModel standard endpoint and returned model alias `glm-4.7`. No immutable
underlying model revision or provider sampling seed was available. Official
[compatibility documentation](https://docs.bigmodel.cn/cn/guide/develop/claude/introduction)
and [pricing](https://docs.bigmodel.cn/cn/guide/start/pricing) were verified and
retained with hashes. The standard endpoint avoided conflating subscription
tool allowances with metered API pricing. No credential configuration changed.

The authorization was bounded more tightly to 112 total attempts, zero retries,
1,200 output tokens per attempt, an 8,192-token conservative input reservation
and a 90-second request timeout. The full planned reserve was CNY 5.820416,
conservatively treated as at most US$5.820416 using a deliberately excessive
one-to-one conversion. This was a ceiling calculation, not an exchange-rate
quotation. Calls without usage reserve the entire per-attempt amount.

Actual accounting is **60 attempts, 59 API responses, 58 executable responses,
one division-by-zero failure and one connection failure**, with **zero retries**.
Known usage is **18,294 input and 6,999 output tokens**. Tier-aware public-price
estimation, including the failed-call reserve, is **CNY 0.1507174**; the higher
4/16-per-million-rate accounting is **CNY 0.237128**. These are estimates, not an
account invoice. The replay uses the frozen higher-rate units; the tier-aware
ledger is also provided. Sum of request wall times is **516.18 seconds**,
including local evaluation; recorded training execution totals **22.10 seconds**.
Replayed per-policy time is reconstructed from observed request durations, not
separately measured online search wall time.

Among all available executable responses, 29 improve on their own parent,
representing 21 distinct training action signatures. Only **one** beats the
initial global training best. There are 58 distinct valid source hashes but
only 33 distinct valid training action signatures. These distinctions prevent
textual novelty and improvements over weak parents from being counted as new
discoveries. See [accounting](../../experiments/metamuse_llm_pilot/accounting_final.json),
[tier-aware prices](../../experiments/metamuse_llm_pilot/nominal_price_accounting.json) and
[candidate evaluations](../../experiments/metamuse_llm_pilot/candidate_evaluations.csv).

Attempt 60 failed with WinError 10060 before a usable HTTP response. The runner
stopped without a retry or endpoint fallback, as specified. Whether that request
reached the provider is unknown; its full reserve stays charged. The
[stop record](../../experiments/metamuse_llm_pilot/EXECUTION_STOP.md) explains why the
comparison is incomplete. Unused authorization was not converted into another
paid round.

Generated programs ran only in a closed scalar AST interpreter, without Python
exec/eval, imports, host objects, file/network access, loops or recursion.
Source, AST, operation, numeric and workload bounds apply; the time check is
cooperative between bounded traces. Forty-eight direct packing conformance
cases and 40 scalar reference cases passed. A four-response parser correction
accepted unique code blocks surrounded by prose and repaired an overly strict
numeric-base bound; it required no extra calls and preserved the original
records. A verifier correction distinguished normalized source hashes from
Windows file-byte hashes. Neither correction changed policies or workloads.

The final [verification](../../experiments/metamuse_llm_pilot/verification.json) confirms
identity, usage, budget and selection/test hash checks; all available training-
valid candidates also execute on the test split. Thirty prior-pilot artifacts
match their original manifest. The upstream MetaMuse checkout remains clean.
Raw [requests and responses](../../experiments/metamuse_llm_pilot/calls), programs,
workloads, failures and frozen intermediate results are preserved. No new
mechanism is promoted, and no test-driven paid continuation was run.
The [final byte-hash manifest](../../experiments/metamuse_llm_pilot/FINAL_MANIFEST.json)
identifies the saved artifacts; the artifact guide provides a no-cost
reproduction command that preserves the balanced selection file.
