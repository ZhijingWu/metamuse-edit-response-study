# MetaMuse: method and released-code analysis

**Finding:** MetaMuse already does feedback-driven stimulus selection and performance-grounded exploration. The official ICLR supplement implements substantially more of that method than the current GitHub entry point. Adding a GP, historical feedback, external hints, or ordinary reflection is not a new direction. Audited **20 October 2026**; the NetArena NO-GO remains unchanged.

## Evidence identity

| Artifact | Verified version and scope |
|---|---|
| [Official ICLR publication](https://proceedings.iclr.cc/paper_files/paper/2026/hash/85632be2cd69e9a0ef4ba054c096fac9-Abstract-Conference.html) | Complete 23-page proceedings PDF, including appendices; SHA-256 `281095ce95392e38371c113acbad902d9d2b0b6c864144c555b09f335ae0e1b4`. Identical bytes to `paper.pdf` in the pinned repository. |
| [arXiv](https://arxiv.org/abs/2510.03851v2) | v2, 16 April 2026, 23 pages; reused local copy. Extracted text was compared with the proceedings version: arXiv header and minor extraction differences, not a different method. |
| [Author-linked repository](https://github.com/illinois-nsai/MetaMuse/tree/b976a28426268e2f7310b0a8d9c33f3a82496479) | HEAD `b976a28426268e2f7310b0a8d9c33f3a82496479`; cloned for reading; no repository edits. Authorship route: official project/publication links and matching paper/authors. |
| [Official ICLR supplement](https://proceedings.iclr.cc/paper_files/paper/2026/file/85632be2cd69e9a0ef4ba054c096fac9-Supplemental-Conference.zip) | 74,912-byte source ZIP; SHA-256 `eeae009105958c60913950c05f42fb935b64d6710d19b6453ca7755c88d03ec1`. Inspected separately under `work/MetaMuse-supplement`. No commit asserted for this archive. |
| [Project website](https://illinois-nsai.github.io/MetaMuse/) / [Yan publications](https://fyy.cs.illinois.edu/publications/) | Confirm the research identity and context. Website summaries are not a substitute for executable-source evidence. |

The supplement matters: a conclusion based solely on the GitHub `run.py` would incorrectly characterize paper mechanisms as wholly unimplemented. Neither release is proven to be the exact environment that produced every paper figure.

## What the paper solves

1. **Collapse:** repeated LLM sampling concentrates around familiar heuristics. The paper interprets this as availability bias and provides model/task evidence; it does not establish a universal causal explanation of every generation failure (§2).
2. **Divergence:** unrelated external words are mapped to properties and then task observations. The system develops these into a design and executable code. Different names or descriptions alone do not establish a different algorithm (§3.3).
3. **Feedback representation:** a solution is represented by performance across workloads. Equal vectors mean equal measured performance on those workloads; they do not prove semantic equivalence, structural novelty, or equal potential under future mutations (§3.1).
4. **Learning:** RSDict samples stimuli independently. RSDict-SF predicts feedback from embeddings of stimulus-derived observations, using Gaussian processes and two sampled stimulus sets. Exploration seeks distance from prior feedback; exploitation seeks good performance. This already changes future generation using history (§3.2).
5. **Waypoints:** property extraction → problem mapping → solution formulation → code generation. Mapped observations, rather than arbitrary words used as variable names, are intended to support useful conceptual changes (§3.3).
6. **Budget:** the study targets 350 executable solutions per method; costs include mapping, design and coding tokens. This is not a proof of compute-optimal allocation. Mapping caches and failed/retried coding affect actual resource use (§4.3).
7. **Evidence:** cache replacement and online bin packing show improved measured solution performance and feedback-space diversity. These are distinct outcomes; neither universally certifies structural novelty. The cache case studies provide interpretable examples, not a complete semantic novelty test (§§4.1–4.4).
8. **Ablations:** removing waypoints reduces diversity; RSDict-SF improves over random dictionary steering; task-related keywords are weaker than the broader dictionary in the reported comparison. These support the components in those settings, not their indispensability for all tasks (§4.5, appendix E).
9. **Failure/cost:** invalid code, excessive execution/memory costs and expensive multi-trace benchmarking remain concerns. The paper reports about 2.28% unsafe outputs and describes safeguards. It explicitly discusses iterative refinement as complementary future integration (§5).
10. **Generalization:** 30 synthetic feedback workloads are described separately from 96 cache and 288 bin-packing evaluation workloads. This is not simply training and testing on the same traces. However, selecting/reporting top candidates over evaluation workloads does not establish a further untouched test set for that selection. Exact split/manifests and all selection decisions are needed for a reproduction (§4).

## Two implementations, not one blended path

| Component | Pinned GitHub path | Official supplement evidence |
|---|---|---|
| Generation | `src/rsdict.py:101–155`: cached word mapping, design JSON, code, evaluation, record | `cache_app/RSDict.py`, `RSDictSF.py`: analogous cache pipeline |
| Actual prompts | `src/problem.py` renders task files; cache callbacks and BPP `select_bin`/`update_after_select` | Cache prompt templates and PlanSearch prompts included |
| Feedback dimensions | `run.py` passes **one folder-aggregating simulator** into `FeedbackEmbedding([simulator])`; the default CLI therefore gives a one-dimensional vector | `cache_app/FeedbackEmbedder.py:24–118` constructs one simulator per supplied trace, normalizes against Belady and returns a vector |
| Stimulus/history selection | `src/gpr.py:104–150`: after 100 valid records, default `window_size=2` keeps the **last two training entries**, then chooses lowest predicted mean | `RSDictSF.py:187–240`: `window_size=2` means **two proposed stimulus sets**, training uses the complete entry list. `GPRSimulator.py:168–191` implements exploratory distance and exploitative mean scoring |
| Exploration schedule | No explore/exploit target switch in the inspected selector | Supplement switches mode by attempt count modulo the 100-attempt warmup interval; this is implemented, not a new extension to propose |
| Diversity count | No comparable analysis suite in the default CLI | `DiversityMetric.py:14–24` rounds feedback coordinates into categories; granularity matters |
| Models | `src/llm.py`: Azure-compatible OpenAI/Llama/DeepSeek endpoints; coding uses the selected supplier too | Coding agent fixed to OpenAI while ideation supplier varies, consistent with the paper's common coding-model comparison |
| Storage | `Entry`: hints, design, code-file path, evaluation metadata, feedback; JSONL plus statistics and response logs | Richer entry schema and nine human-baseline records; no released generated-candidate archive located |
| Stopping/cost | `llm_call_counter` increments once per **entry attempt**, including failures; actual API calls include mapping, retries, design and coding | Same distinction between entry count and underlying API/token cost |

Source links: [GitHub runner](https://github.com/illinois-nsai/MetaMuse/blob/b976a28426268e2f7310b0a8d9c33f3a82496479/run.py), [generation](https://github.com/illinois-nsai/MetaMuse/blob/b976a28426268e2f7310b0a8d9c33f3a82496479/src/rsdict.py), [GP selector](https://github.com/illinois-nsai/MetaMuse/blob/b976a28426268e2f7310b0a8d9c33f3a82496479/src/gpr.py), [feedback](https://github.com/illinois-nsai/MetaMuse/blob/b976a28426268e2f7310b0a8d9c33f3a82496479/src/feedback_embedding.py), and the hashed official supplement above. These release differences are reproduction findings, **not algorithmic novelty**.

## Evaluation and reproducibility boundaries

GitHub BPP loads an instance and `l1_bound` from a pickle, executes a policy, checks feasibility/conservation, and minimizes `100 × (bins − l1_bound)/l1_bound`, averaged over traces (`simulators/bpp_core.py:94–129`, `bpp_online.py:47–56`). The label `miss_ratio` used by the generic interface does not change that meaning. The CPU pilot preserves this BPP objective and forced-new-bin behavior, using newly generated JSON workloads rather than untrusted pickles.

The cache runner executes a policy module once, then creates caches for the trace sequence. Policy-global metadata may persist across traces; no general policy reset hook is established there. Both task prompts require read-only snapshots and deterministic behavior, while the core exposes mutable Python objects. These are control/isolation questions for an exact reproduction, not evidence of a published exploit. No arbitrary generated program or full upstream runner was executed in this work.

No benchmark traces are included in the inspected GitHub tree or supplement. The latter includes nine baseline records but references missing dictionary/package paths (`nips2025`, `en_dict`) and external cache tooling/data. Public storage/BPPLIB sources are cited by the paper; **absence from the archive does not mean they are proprietary**. Exact preprocessing, selected files, private production deployment resources and a complete author run archive remain unverified. Production deployment is ongoing work in the paper, not a prerequisite demonstrated for the released experiments.

Available modules can support an independent generator/evaluator/selector adapter. Changing stimulus acquisition is localized; adding parent-based mutation requires a new refinement stage because native MetaMuse does not mutate an archive parent. A source-compatible adapter is feasible, but not a one-line replacement or evidence of an existing parent-selection API. The supplement's historical dependencies and the current runner's Unix `SIGALRM` timeout also prevent calling this a verified Windows end-to-end reproduction.

**Research implication:** performance-space diversity is a useful operational descriptor, but whether it preserves information needed for subsequent algorithm refinement is a separate question. The next reports test that question without claiming MetaMuse deletes equivalent programs or lacks feedback learning.
