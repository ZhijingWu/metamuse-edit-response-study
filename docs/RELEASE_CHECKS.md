# Release checks

Checked from the public staging tree, independently of the original workspace's result paths:

- Python 3.13.5, standard library only; dependency installation needs no package download.
- CPU transition count 5,628/5,655; all 420 cached comparison rows agree with the original first and corrected second pilots.
- Interrupted pilot: all 1,400 balanced-subset selection rows and held-out lookups agree, with no model calls.
- Continuation: all twelve exact 32-credit comparison rows and sixty curve/priced rows agree in outcomes, spending, coverage and scientific decisions. The wrapper writes new selector-computation timing only to ignored reproduction output.
- Restricted evaluator: 96 existing seed/trace bin counts agree with the released results.
- Figure values match the exact CSV. Both TikZ sources remain vector artwork.
- Note compiled successfully: exactly two US Letter pages; no overfull/underfull boxes; clickable repository URI. Both pages were rendered and visually inspected. Only the final evidence paragraph changed from the approved scientific note.
- The staged security scan found no configured credential value, recognized token/private-key pattern, private user path, sensitive provider envelope field, unexpected binary, or oversized file. All 121 extracted model candidate programs were inspected by the bounded candidate-source checks described in the publication audit.
- Root license applies to original material only. Upstream source, downloaded papers/provider documentation and full provider envelopes are excluded; generated records have separate provenance and are not blanket relicensed.

Run `python -B tools/reproduce.py verify` to check the public byte manifest and `python -B tools/reproduce.py all --out .reproduced/new_check` for the supported offline checks. The manifest is an integrity record, not a claim of independent authorship or a cryptographic signature. No replay draw is counted as a new LLM experiment.
