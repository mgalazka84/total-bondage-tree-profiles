"""Small reproducible benchmarks; not evidence for the asymptotic theorem."""
import csv
from pathlib import Path
import random
import time
import networkx as nx
from bondage import bondage_profile


if __name__ == '__main__':
    rows = []
    for n in (16, 32, 64, 128):
        rng = random.Random(291026+n)
        cases = [('path', nx.path_graph(n)), ('star', nx.star_graph(n-1)),
                 ('prufer', nx.from_prufer_sequence([rng.randrange(n) for _ in range(n-2)]))]
        for label, tree in cases:
            edges = sorted(tuple(sorted(e)) for e in tree.edges())
            start = time.perf_counter()
            answer = bondage_profile(n, edges, witnesses=False)
            row = {'family': label, 'n': n, 'seconds': round(time.perf_counter()-start, 6),
                   'peak_states': answer['peak_states'],
                   'candidate_pairs': answer['candidate_pairs']}
            print(row, flush=True)
            rows.append(row)
    Path('results').mkdir(exist_ok=True)
    with Path('results/benchmarks.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
