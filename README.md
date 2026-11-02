# Total bondage profiles of trees

Exact Python code for computing all minimum edge-deletion costs that increase
the total domination number of a tree by at least `k`, while leaving no isolated
vertices. All dominating vertices have unit cost; deletion costs may be
nonnegative integers or exact rational numbers.

This repository contains code and reproducible computational results. The
research manuscript and submission materials are maintained separately.

## Quick start

Python 3.10 or later is required. The core solver uses only the standard library.

```bash
python bondage.py --path 8
```

From Python:

```python
from fractions import Fraction
from bondage import bondage_profile

edges = [(0, 1), (1, 2), (2, 3)]
answer = bondage_profile(4, edges)
assert answer['gamma'] == 2
assert answer['profile'] == [0, 1, 1]

weighted = bondage_profile(4, edges, costs=[2, Fraction(3, 2), 7])
assert weighted['profile'] == [0, Fraction(3, 2), Fraction(3, 2)]
```

Vertices are numbered `0,...,n-1`. The input must be a simple tree with `n >= 2`.
The returned profile includes `k=0`. Unattainable targets are `math.inf`; the
command-line JSON uses `null`. Each witness is a tuple of indices into the
original edge list, not a tuple of vertex pairs. Passing `witnesses=False`
disables predecessor storage. The answer is independent of the chosen `root`.

## Reproduce the verification

```bash
python -m pip install -r requirements.txt
python verify.py --max-n 12 --output results
python families.py
python benchmark.py
python state_counts.py
python revision_checks.py
python make_figures.py
```

The full run checks:

- all 986 nonisomorphic trees of orders 2 through 12;
- 18,556 admissible residual graphs, using an independent exhaustive oracle;
- 247 additional weighted instances, including zero and fractional costs;
- 278 additional choices of root;
- every finite optimum's deletion witness;
- the terminal formula involving the matching number;
- the exact spider-family profile for `r=1,...,30`.

The recorded verification has zero failures. `results/verification.json` records
the Python and NetworkX versions and per-order counts. Times are machine
dependent. `results/all_profiles.csv` records every unweighted profile, with
`null` for infinity. Figures are regenerated in `figures/` from exact data.

The independent oracle in `bruteforce.py` enumerates deletion sets and then
vertex subsets; it never calls the dynamic program. The primary solver retains
complete four-entry boundary signatures and the cheapest deletion realization
of each signature. It uses sparse dictionaries; the deterministic O(n^4)
arithmetic-operation proof uses the corresponding direct-address encoding.
Expected constant-time hash lookup gives the same O(n^4) operation bound in
expectation for the sparse implementation.

## Observed signature-table sizes

`peak_states` is the largest number of signatures in any one intermediate or
completed table during a run. `state_counts.py` summarizes the recorded counts
in `results/state_counts.json`, including input-file hashes. The maxima for the
exhaustive tree sets of orders 2 through 12 are respectively
`1, 1, 2, 3, 5, 5, 10, 14, 22, 24, 33`.

| Order | Path | Star | Pruefer tree | Spider |
| --- | --- | --- | --- | --- |
| 16 | 34 | 1 | 19 | 38 |
| 32 | 82 | 1 | 88 | 110 |
| 64 | 178 | 1 | 154 | 254 |
| 128 | 370 | 1 | 355 | 542 |

These recorded runs use root 0. Exhaustive and benchmark runs use sorted edge
lists; spider runs process the long arm before the short arms. Each Pruefer
tree uses the single sequence generated with seed `291026+n`. Counts can depend
on the root and child order, although the profile does not. The finite data do
not establish whether the quadratic worst-case state bound is tight.

## Files

| File | Purpose |
| --- | --- |
| `bondage.py` | Standard-library solver and witness reconstruction |
| `bruteforce.py` | Independent exponential oracle |
| `verify.py` | Exhaustive and weighted comparisons |
| `families.py` | Exact-profile checks for the spider family |
| `benchmark.py` | Reproducible small timing experiments |
| `state_counts.py` | Summary of recorded signature-table sizes |
| `revision_checks.py` | Independent checks of clarified lemma and weighted terminal value |
| `make_figures.py` | Exact network diagrams and profile plots |
| `results/` | Recorded results |

## Research context

- J.-P. Appel et al., *The k-Total Bondage Number of a Graph*, Theory &
  Applications of Graphs 13(1), Article 3 (2026).
  <https://doi.org/10.20429/tag.2026.130103>
- N. Jafari Rad and J. Raczek, *Some Progress on Total Bondage in Graphs*,
  Graphs and Combinatorics 30, 717–728 (2014).
  <https://doi.org/10.1007/s00373-013-1303-2>
- S. Bahadır, *Graphs with Total Domination Number Double of the Matching
  Number*, Journal of New Theory 49, 1–6 (2024).
  <https://doi.org/10.53570/jnt.1520557>

The matching equality characterization belongs to Bahadır. The k=1 tree problem
predates this project. This project concerns explicit full-profile computation
with edge costs and an exact spider-family example. Computational verification
supports the implementation; it does not replace mathematical proofs.

## License

MIT. AI assistance was used in developing and checking the computational code.
