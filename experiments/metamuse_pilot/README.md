# Finite-grammar CPU study

The first bank is in `results/`; the revised collision-triggered comparison's authoritative bank is `selective_results_corrected/`. `selective_results/` retains the superseded implementation/results, explicitly excluded from headline claims. All programs are coefficient tuples, not model generations.

Use `python -B tools/reproduce.py cpu --out .reproduced/cpu_check` from the repository root. It replays the two completed comparisons against retained matrices without regenerating workloads, candidates or model outputs. See [reproduction documentation](../../docs/REPRODUCIBILITY.md).

The historical `pilot.py` main routine additionally performs an optional upstream conformance check against a separate MetaMuse checkout. That dependency is not vendored and is not required by the supported public replay command. Do not treat this independent grammar study as an official MetaMuse reproduction.
