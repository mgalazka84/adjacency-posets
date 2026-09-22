# Adjacency posets of cocomparability graphs and small outerplanar obstructions

Marek Gałązka and Hanna Wdowicka

Supplementary code and data, 22 September 2026.

Repository: [https://github.com/mgalazka84/adjacency-posets](https://github.com/mgalazka84/adjacency-posets).

The associated manuscript proves the exact formula for adjacency-poset dimension on cocomparability graphs and classifies the seven smallest maximal outerplanar obstructions of dimension four. This supplement contains the finite certificates and construction algorithms.

## Check the results

Use Python 3.10 or newer, from this directory:

```sh
python verify_all.py
```

This command requires **only the Python standard library**. Run Python normally, without `-O`, because the checker uses assertions. The expected final line is:

```text
ALL CERTIFICATE CHECKS PASSED
```

The checker verifies:

- 1092 maximal outerplanar graphs on 3 through 12 vertices;
- 776 explicit three-extension realizers, checking all ordered pairs of poset elements;
- 316 proofs that necessary reversal-color constraints are inconsistent;
- completeness of the graph list using an independent ear-insertion generator;
- all 70 single-vertex deletions of the seven ten-vertex obstructions;
- a pair of graphs with isomorphic weak duals and different dimensions;
- all supplied explicit implication chains;
- realizers for exactly the 152 graphs whose weak dual is a path.

The lower certificates establish dimension at least four by color rigidity and conflicting reversals. Equality uses Witkowski's published upper bound for outerplanar graphs. A satisfiable conflict-list instance is **not** treated as a proof of dimension at most three.

## Encoding

Graph vertices are `0,...,n-1`, in their outer-cycle order. Every graph in `experiments.json` contains the cycle `0,1,...,n-1,0`. Its canonical edge list is the lexicographically least list under rotations and reflections. The `index` is its zero-based position among the sorted canonical lists of that order.

The adjacency poset has elements `0,...,2*n-1`. Integer `v` denotes the lower copy of vertex `v`; integer `n+v` denotes its upper copy. Its only strict comparisons are `u < n+v` for graph edges `uv`. A stored order is read from first to last.

The colors in the data are `0,1,2`. The constraints and proofs may fix an indexing of the realizer using these colors; the full-order checker does not depend on that symmetry assumption.

## Validate the general chain construction

```sh
python verify_small_poset_chains.py
```

This separate standard-library check covers all naturally labeled posets with at most five elements and all partitions into nonempty chains: 407 posets and 3817 partitions. It checks the full intersection of the constructed linear orders, including non-interval cases. Its output is in `small_poset_chains_verification.log`. The finite check validates the implementation; the theorem for arbitrary finite cocomparability graphs is proved in the manuscript.

## Files

| File | Purpose |
|---|---|
| `experiments.json` | All 1092 canonical MOP graphs and positive realizers |
| `negative_certificates.json` | 316 integer-only lower-bound certificates |
| `certificates.py`, `verify_all.py` | Independent certificate verification and coverage check |
| `vertex_deletion_realizers.json` | All 70 single-vertex deletion certificates |
| `weak_dual_counterexample.json` | Graphs, realizer and weak-dual isomorphism |
| `implication_certificates.json` | Explicit short implication proofs for four obstructions |
| `outerpath_realizers.json` | 152 constructive realizers, interval models and chain partitions |
| `constructions.py` | General chain-based and interval-based constructions |
| `verify_small_poset_chains.py` | Exhaustive validation of the general construction on small posets |
| `research.py`, `structural.py`, `proof_tools.py` | Discovery and structural routines |
| `regenerate_auxiliary.py` | Regeneration of deletion and weak-dual certificates |
| `requirements-search.txt` | Optional SAT-search dependency |
| `verification.log`, `small_poset_chains_verification.log` | Validation outputs |
| `SHA256SUMS` | Checksums of the distributed files |

The three entries with `paths: null` in `implication_certificates.json` are intentional. Their lower bounds use the full critical-pair certificates, including same-layer pairs.

## Reproduce discovery

In a working copy, install the optional search dependency and run:

```sh
python -m pip install -r requirements-search.txt
python research.py 12
python certificates.py produce
python regenerate_auxiliary.py
python proof_tools.py
python constructions.py
python verify_all.py
```

The discovery procedure uses PySAT/Glucose4. No solver or network is needed to verify the supplied certificates. An optional MILP routine in `research.py` uses NumPy and SciPy; it is not used as a lower-bound certificate. Different solver versions may produce different valid realizers.

## Scope and provenance

The minimum order ten is established within the maximal outerplanar class. The data do not establish a complete obstruction characterization for all orders. A satisfiable two-pair conflict instance is not treated as proof of dimension three; every positive instance has a full realizer.

ChatGPT (OpenAI, September 2026) assisted mathematical exploration, programming, proof checking and manuscript preparation. The supplied verification works directly with the combinatorial definitions and explicit certificates. Computational independence refers to the checker versus the discovery solver.

## Citation

If you use this code or data, please cite version 1.0.0:

> Marek Gałązka and Hanna Wdowicka (2026). *Adjacency posets of cocomparability graphs and small outerplanar obstructions*. Supplementary software and data, version 1.0.0.

Machine-readable citation metadata are provided in `CITATION.cff`.
