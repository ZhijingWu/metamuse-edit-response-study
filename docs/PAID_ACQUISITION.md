# Historical paid acquisition is separate from reproduction

Every supported command in `REPRODUCIBILITY.md` is offline and blocks network connections. No default install, verification, replay, figure or note command calls a model.

For source inspection, the original acquisition implementations are retained in:

- `experiments/metamuse_llm_pilot/llm_pilot.py`, function `acquire(stage)`.
- `experiments/metamuse_continuation/continuation.py`, function `acquire(stage)`.

The historical explicit CLI forms were:

```text
python experiments/metamuse_llm_pilot/llm_pilot.py acquire --stage <declared-stage>
python experiments/metamuse_continuation/continuation.py acquire --stage <declared-stage>
```

These commands are **paid acquisition, not reproduction instructions**. They require a separately configured credential in the environment, explicit stages, code/config identity and stage-boundary checks. Do not run them against this completed archive. Existing freeze/stop records prevent normal resumption; sanitized development hashes are not a new prospective protocol. Credentials are not distributed. No SDK retries or fallback provider is installed.

A new paid study would need its own empty acquisition directory, frozen protocol, reviewed current terms/pricing, explicit call/spend/retry ceilings and untouched outcome set. That future setup is not implemented or validated by the public replay entry point. Changing a model alias and issuing new stochastic calls is not exact reproduction of these recorded programs. The completed study calls for no additional tuning round.
