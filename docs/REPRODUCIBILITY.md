# Offline reproducibility

Run these commands from a fresh clone, using Python 3.10 or newer. The release was checked with Python 3.13.5. There are no third-party Python dependencies:

```sh
python -m pip install --no-index -r requirements.txt
python -B tools/reproduce.py verify
python -B tools/reproduce.py all --out .reproduced/check
python -B tools/recreate_figures.py
```

`all` runs the following independently available checks:

```sh
python -B tools/reproduce.py cpu --out .reproduced/cpu_only
python -B tools/reproduce.py initial
python -B tools/reproduce.py continuation --out .reproduced/continuation_only
python -B tools/reproduce.py evaluator
```

The output must be below `.reproduced/`; reuse of a nonempty replay destination is refused. Network connection methods are disabled before importing study modules. No credential is read by these entry points. Acquisition functions are never invoked. Use `-B` to avoid untracked bytecode files.

## What is reproduced

1. **Manifest:** byte hashes and complete file coverage of the public release. The manifest excludes itself, `.git`, bytecode and ignored reproduction outputs. This is a content check, not an external cryptographic signature.
2. **CPU:** recalculate exact grammar transition counts from the retained score/bin matrices; replay all 270 first-pilot and 150 corrected second-pilot selection rows; compare training/test costs, program identity and charged requests to the frozen CSVs. This is cached-bank replay, not 420 newly acquired banks. The superseded second-pilot results remain labeled separately.
3. **Initial LLM pilot:** reconstruct 1,400 selection rows from the complete balanced 48-attempt subset (16 probes plus four future edits per eight parents), and verify held-out lookups. All 60 actual attempts remain in accounting. The planned full comparison endpoint remains incomplete.
4. **Continuation:** reconstruct 560 conditional allocation choices across twelve selectors and five budget views, recompute exact finite-subset expectations at 32 credits, and recalculate the held-out tables from recorded outcomes. Compare all twelve exact rows and sixty curve/priced rows to the release. Host selector-computation timings can change; recorded generation/evaluation costs, outcomes and scientific decisions are retained. Timing is not claimed bit-identical across computers.
5. **Evaluator:** re-evaluate the eight existing human seeds on the twelve original training traces and compare all 96 bin counts. This deterministic verification uses the restricted AST interpreter; it never executes generated Python as host code.

`replay_training.json.gz` decompresses to the original replay JSON byte stream. The reproducibility loader reads it directly; users need not store a second large copy. `comparison_rows.json` is omitted because the continuation replay regenerates it from retained selections and trace results. No essential score, program, workload or failed outcome is imputed.

## Figures and note

```sh
python -B tools/recreate_figures.py
cd notes
pdflatex --disable-installer -interaction=nonstopmode -halt-on-error Zhijing_Wu_MetaMuse_Search_Representation_Note.tex
```

The figure command verifies every plotted numerical value against the exact CSV and writes the existing vector sources below `.reproduced/figures/`. Figure 1 is explicitly illustrative. Figure 2 is a numeric table, without invented error bars. The note builds both TikZ figures directly, so no raster or image-generation service is required.

Note compilation additionally requires a TeX distribution with NewTX, Helvetica, TikZ, geometry, multicol, microtype, caption, fancyhdr, titlesec and hyperref. The included PDF is usable without TeX. It has exactly two pages. Recompilation may change PDF creation metadata and byte hashes even when the scientific content is identical; run it in a working copy if verifying the release manifest afterward.

## Boundaries

This reproduces recorded-output evaluation and selection comparisons, not independent stochastic model generation. GLM-4.7 is a provider alias, not an immutable model revision; there was no provider sampling seed. Historical costs are token-price estimates, not account billing statements. Eight fresh workload banks quantify workload sampling conditional on one model-search matrix. Neither 100 nor 560 allocation replays are independent LLM searches.

The development CPU script's optional `conformance()` reads two classes from the separately obtained official MetaMuse checkout at commit `b976a28426268e2f7310b0a8d9c33f3a82496479`. That upstream code is not redistributed and is **not required by the tested public commands**. The official repository is [illinois-nsai/MetaMuse](https://github.com/illinois-nsai/MetaMuse); inspect its applicable rights before obtaining/reusing its files. We do not claim a self-contained rerun of upstream MetaMuse or its benchmark preparation.

Historical scripts and reports may describe original workspace-relative commands, original byte hashes and intermediate states. The entry points above are the supported portable commands. Original development manifests identify provenance; the public `ARTIFACT_MANIFEST.json` identifies the sanitized release. [Export map](../provenance/EXPORT_MAP.json) records exclusions and transformations.
