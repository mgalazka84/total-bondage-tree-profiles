"""Independent small checks for the clarified spider and terminal statements."""
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import networkx as nx
from bruteforce import profile, total_domination


def weighted_terminal_star_cost(tree, costs):
    """Enumerate deletions and recognize terminal star forests directly."""
    edges = sorted(tuple(sorted(e)) for e in tree.edges())
    candidates = [i for i, (u, v) in enumerate(edges)
                  if tree.degree(u) > 1 and tree.degree(v) > 1]
    nu = len(nx.max_weight_matching(tree, maxcardinality=True))
    best = None
    for count in range(len(candidates) + 1):
        for chosen in combinations(candidates, count):
            removed = set(chosen)
            residual = nx.Graph()
            residual.add_nodes_from(tree.nodes())
            residual.add_edges_from(e for i, e in enumerate(edges) if i not in removed)
            components = list(nx.connected_components(residual))
            if len(components) != nu:
                continue
            if any(len(c) < 2 or max(residual.degree(v) for v in c) != len(c)-1
                   for c in components):
                continue
            cost = sum((costs[i] for i in removed), Fraction(0))
            best = cost if best is None else min(best, cost)
    return best


def run():
    spider_checks = []
    for length in range(13):
        edges = [(i, i+1) for i in range(length)]
        edges += [(0, length+1), (length+1, length+2),
                  (0, length+3), (length+3, length+4)]
        n = length + 5
        # Integer form of the stated residue formula.
        h = length//2 if length % 2 == 0 else 2*((length//2+1)//2)
        actual = total_domination(n, edges)
        assert actual == 3+h, (length, actual, h)
        spider_checks.append({'arm_length': length, 'n': n, 'gamma': actual})

    weighted_checks = 0
    for n in range(2, 9):
        for tree in nx.nonisomorphic_trees(n):
            edges = sorted(tuple(sorted(e)) for e in tree.edges())
            costs = [Fraction(i % 5, (i % 3)+1) for i in range(n-1)]
            answer = profile(n, edges, costs)
            nu = len(nx.max_weight_matching(tree, maxcardinality=True))
            terminal = 2*nu-answer['gamma']
            expected = weighted_terminal_star_cost(tree, costs)
            assert answer['profile'][terminal] == expected
            weighted_checks += 1

    edges = [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4)]
    graph = nx.Graph(edges)
    answer = profile(5, edges)
    nu = len(nx.max_weight_matching(graph, maxcardinality=True))
    terminal = 2*nu-answer['gamma']
    actual = answer['profile'][terminal]
    assert (nu, answer['gamma'], terminal, actual) == (2, 2, 2, 1)
    assert actual != len(edges)-len(graph)+nu

    return {
        'spider_lemma': spider_checks,
        'weighted_terminal_instances': weighted_checks,
        'weighted_costs': 'Fraction(i % 5, (i % 3)+1) for sorted edge index i.',
        'triangle_hypothesis_counterexample': {
            'n': 5, 'edges': edges, 'matching': nu, 'gamma': answer['gamma'],
            'terminal_threshold': terminal, 'terminal_cost': actual,
            'm_minus_n_plus_matching': len(edges)-len(graph)+nu,
        },
        'failures': 0,
    }


if __name__ == '__main__':
    result = run()
    destination = Path(__file__).resolve().parent / 'results' / 'revision_checks.json'
    destination.write_text(json.dumps(result, indent=2)+'\n')
    print(f"Verified {len(result['spider_lemma'])} spider-lemma cases, "
          f"{result['weighted_terminal_instances']} weighted terminal instances, "
          "and the triangle counterexample; zero failures.")
