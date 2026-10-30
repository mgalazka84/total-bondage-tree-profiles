"""Exhaustive comparison against independent subset enumeration."""
import argparse
import csv
from fractions import Fraction
import json
from math import inf
from pathlib import Path
import platform
import time
import networkx as nx
from bondage import bondage_profile
from bruteforce import profile as oracle, total_domination


def clean(x):
    if isinstance(x, dict):
        return {str(k): clean(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set, frozenset)):
        return [clean(v) for v in x]
    if x == inf:
        return None
    if isinstance(x, Fraction):
        return str(x)
    return x


def check_witnesses(n, edges, costs, result):
    for k, (value, removed) in enumerate(zip(result['profile'], result['cuts'])):
        if value == inf:
            assert removed is None
            continue
        assert sum(costs[i] for i in removed) == value
        remaining = [e for i, e in enumerate(edges) if i not in removed]
        achieved = total_domination(n, remaining)
        assert achieved != inf and achieved >= result['gamma'] + k


def run(max_n, output):
    output.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    counts, rows, examples = [], [], {}
    total_trees = weighted = rooted = cut_count = 0
    collisions = {}
    for n in range(2, max_n+1):
        tick = time.perf_counter()
        ntrees = ncuts = 0
        for number, tree in enumerate(nx.nonisomorphic_trees(n)):
            edges = sorted(tuple(sorted(e)) for e in tree.edges())
            brute = oracle(n, edges)
            result = bondage_profile(n, edges)
            assert result['gamma'] == brute['gamma'], (n, number, 'gamma')
            assert result['profile'] == brute['profile'], (n, number, 'profile')
            check_witnesses(n, edges, [1]*(n-1), result)
            matching = len(nx.max_weight_matching(tree, maxcardinality=True))
            max_k = max(k for k, x in enumerate(result['profile']) if x != inf)
            assert max_k == 2*matching-result['gamma']
            assert result['profile'][max_k] == matching-1
            for k, x in enumerate(result['profile']):
                if x != inf:
                    assert x >= (k+1)//2
            if n <= 10:
                costs = [((3*i+number) % 8) for i in range(n-1)]
                weighted_result = bondage_profile(n, edges, costs)
                weighted_brute = oracle(n, edges, costs)
                assert weighted_result['profile'] == weighted_brute['profile']
                check_witnesses(n, edges, costs, weighted_result)
                weighted += 1
            if n <= 8:
                for root in range(1, n):
                    again = bondage_profile(n, edges, root=root, witnesses=False)
                    assert again['profile'] == result['profile']
                    rooted += 1
                costs = [Fraction(i+1, (i % 3)+1) for i in range(n-1)]
                assert bondage_profile(n, edges, costs)['profile'] == oracle(n, edges, costs)['profile']
                weighted += 1
            if 'nonnested' not in examples:
                for k in range(1, max_k):
                    if not any(a <= b for a in brute['optimal'][k]
                               for b in brute['optimal'][k+1]):
                        examples['nonnested'] = clean({'n': n, 'edges': edges,
                            'gamma': result['gamma'], 'profile': result['profile'],
                            'k': k, 'optimal_k': brute['optimal'][k],
                            'optimal_next': brute['optimal'][k+1]})
            key = (tuple(sorted(dict(tree.degree()).values())), result['gamma'], matching)
            prior = collisions.get(key)
            if prior and prior['profile'] != result['profile'] and 'same_invariants' not in examples:
                examples['same_invariants'] = clean({'first': prior,
                    'second': {'n': n, 'edges': edges, 'profile': result['profile']},
                    'degrees': key[0], 'gamma': key[1], 'matching': key[2]})
            collisions.setdefault(key, {'n': n, 'edges': edges, 'profile': result['profile']})
            rows.append({'n': n, 'index': number, 'gamma': result['gamma'],
                         'matching': matching, 'profile': json.dumps(clean(result['profile'])),
                         'peak_states': result['peak_states'],
                         'candidate_pairs': result['candidate_pairs'],
                         'admissible_cuts': brute['admissible_cuts']})
            ntrees += 1
            ncuts += brute['admissible_cuts']
        total_trees += ntrees
        cut_count += ncuts
        row = {'n': n, 'trees': ntrees, 'admissible_cuts': ncuts,
               'seconds': round(time.perf_counter()-tick, 4)}
        counts.append(row)
        print(json.dumps(row), flush=True)
    report = {'max_n': max_n, 'trees': total_trees,
              'weighted_instances': weighted, 'additional_roots': rooted,
              'admissible_cuts': cut_count, 'failures': 0,
              'python': platform.python_version(), 'networkx': nx.__version__,
              'seconds': round(time.perf_counter()-start, 4), 'by_order': counts,
              'examples': examples}
    (output/'verification.json').write_text(json.dumps(report, indent=2)+'\n')
    with (output/'all_profiles.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--max-n', type=int, default=11)
    parser.add_argument('--output', type=Path, default=Path('results'))
    args = parser.parse_args()
    run(args.max_n, args.output)
