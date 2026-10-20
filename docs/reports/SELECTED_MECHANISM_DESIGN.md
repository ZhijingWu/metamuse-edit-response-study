# Selected mechanism design: edit-conditioned equivalence refinement

**Status:** selected for testing; **not adopted**. The initial response-diversity archive and its collision-triggered revision did not establish an advantage over cheap strong controls. This document specifies the mechanism and the remaining question without presenting a failed pilot as a successful method.

## Precise search object

Let `p` be an executable algorithm, `F(p)` its vector of measured costs on fixed training workloads, and `M_l(p)` the child produced by edit operator `l`. A current-performance cell is `C(p) = bucket(F(p))`. The bucket/normalization must be frozen; equal measured vectors are not full semantic equivalence.

For a fixed randomized proposal kernel `K`, a representation `C` preserves a single-lineage Markov process only if, for every pair in the same cell and every destination cell `D`,

`Pr[C(M(p)) = D] = Pr[C(M(q)) = D]`.

This is the classical lumpability condition, not a new theorem. If within-cell transition distributions differ by at most total-variation `δ` **uniformly across the relevant states**, a stepwise coupling bounds an H-step event-probability discrepancy by `min(1, Hδ)`. Proof sketch: couple each next-cell transition with mismatch probability at most δ; union-bound the first mismatch over H steps. Reward must depend on the represented state. This does **not** automatically apply to adaptive population search or history-dependent LLM prompts: their state must include the archive, prompt/history, model and sampling policy. Two probe edits cannot estimate or certify this uniform bound.

The actionable observation is narrower: **one witnessed response difference refutes a claimed edit-conditioned equivalence**, even though it does not prove which parent is better.

## Implemented responses and archive decision

For a small fixed labeled probe set `L`, form the signed response signature

`R_L(p) = concatenate_l [F(M_l(p)) − F(p)]`.

Unlike a source-code embedding, it measures executed changes. Unlike a scalar offspring-quality/variance statistic, it retains edit identity and per-workload response. Both the choice of edits and workload metric scale matter.

The first prototype used best-preserving farthest-point archive retention over `R_L`. The revision changed the **acquisition rule**:

```text
generate and evaluate a candidate p using the common proposal operator
if p has no same-performance representative q in the active archive:
    apply the common performance-diversity retention rule
else if enough common budget remains:
    evaluate the same two edits of p and q       # four charged probes
    make every probe child eligible as final best-so-far output
    if the two labeled response signatures differ:
        preserve p and q as distinct representatives
        evict the least distinct other member, protecting the best performer
    else:
        apply the common retention rule
else:
    apply the common retention rule
emit subsequent proposals from the resulting fixed-size parent archive
```

The finite grammar uses audited deterministic edits, so differences are exact for those edits/workloads. For LLM edits, repeated samples and a declared decision rule would be required; mismatching single stochastic samples is not evidence of different underlying distributions.

## Inputs, outputs and cost

Observable inputs: candidate code/grammar, legal edit labels, training scores, remaining budget, active archive and measured probe scores. Held-out workloads, exhaustive bank labels and future children are unavailable to the selector. Outputs: which parent representations remain active, which probe to execute, and which evaluated algorithm is returned.

For N proposed primary candidates, c collision events and m edits per representative, an uncached upper cost is `N + 2mc` candidate evaluations; the revision has `m=2`. Token cost, if using LLM edits, includes every probe proposal/retry. Caching must key code, task, traces, state reset and configuration; duplicate generated programs still consume generation tokens even if execution is cached. The local comparison charges repeated evaluation requests but reports unique programs separately. It is a declared conservative budget model, not a measured paid-inference cost.

Response computation is linear in `m × workload_count` once evaluations exist. The prototype's farthest-point selection is ordinary archive machinery. The expensive operation is obtaining trustworthy child scores; no optimization claim follows from cheap descriptor computation.

## Borrowed versus potentially distinct

Borrowed: semantic equivalence, neutral drift, evolvability, per-input feedback, archive diversity, farthest-point retention, matched perturbations and the coupling argument. Quality Evolvability already optimizes offspring properties; Clade-AHD already values descendants. FunSearch already retains multiple same-signature programs. None should be described as missing these general ideas.

Potentially distinct research question: **can inexpensive, selectively acquired edit-response witnesses prevent harmful equivalence decisions at lower total discovery cost than neutral drift, structural diversity and descendant-quality credit?** The targeting of the probe to an actual representation decision is the mechanism to challenge. Its originality and usefulness remain unverified. The observed local revision spent roughly half its budget probing and did not beat neutral drift; a claim of efficient information acquisition is presently unsupported.

## Integration and decisive controls

Use MetaMuse's creative generator unchanged to obtain an initial pool. Add one explicitly shared refinement operator and archive adapter for all experimental arms. Compare the selected retention/acquisition rule with performance-only diversity, structural diversity, random retention, cheap neutral drift, offspring-quality/evolvability and Clade-style credit. Also retain pure MetaMuse creative generation as a later system-level baseline. No current source establishes a native parent-mutation hook; an independent adapter is required.

Hold the initial pool, generator/coder, workload split, edit prompts, total token/evaluation budgets and unrelated selection rules fixed. Randomize request order when a remote model cannot provide paired randomness. Compare against a cost-matched probe control that ignores the response information. A benefit from simply executing more useful candidate probes is not evidence that response-guided retention works.

Failure cases: genotype-coordinate artifacts; metric scaling; probe labels that predict nothing about future edits; missing invalid-child mass; easy tasks where random search saturates; multiple representatives consuming valuable slots; cached duplicates distorting cost; and LLM context changes invalidating the assumed kernel. These are limitations to test, not exceptions allowing positive results to be selected after the fact.

**Decision after local evidence:** do not deploy either tested policy as an improvement. Retain the operator-conditioned question for a narrowly costed real-program test, conditional on novelty and decision value beyond the established competitors.
