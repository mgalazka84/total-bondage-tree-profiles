"""Independent exponential oracle; no recurrence from bondage.py is used."""
from itertools import combinations
from math import inf


def total_domination(n, edges, return_set=False):
    neighbours = [0] * n
    for u, v in edges:
        neighbours[u] |= 1 << v
        neighbours[v] |= 1 << u
    if any(x == 0 for x in neighbours):
        return (inf, None) if return_set else inf
    for size in range(2, n+1):
        for chosen in combinations(range(n), size):
            mask = sum(1 << v for v in chosen)
            if all(mask & hood for hood in neighbours):
                return (size, chosen) if return_set else size
    raise AssertionError('The whole vertex set must dominate an isolate-free graph.')


def enumerate_deletions(n, edges, costs=None):
    edges = list(edges)
    costs = [1] * len(edges) if costs is None else list(costs)
    degree = [0] * n
    for u, v in edges:
        degree[u] += 1
        degree[v] += 1
    # Every admissible deletion set avoids all original pendant edges.
    eligible = [i for i, (u, v) in enumerate(edges) if degree[u] > 1 and degree[v] > 1]
    for mask in range(1 << len(eligible)):
        removed = frozenset(eligible[j] for j in range(len(eligible)) if mask >> j & 1)
        remaining = [e for i, e in enumerate(edges) if i not in removed]
        gamma = total_domination(n, remaining)
        if gamma != inf:
            yield removed, sum(costs[i] for i in removed), gamma


def profile(n, edges, costs=None):
    gamma = total_domination(n, edges)
    out = [inf] * (n-gamma+1)
    optimal = [[] for _ in out]
    count = 0
    for removed, cost, newgamma in enumerate_deletions(n, edges, costs):
        count += 1
        for k in range(newgamma-gamma+1):
            if cost < out[k]:
                out[k], optimal[k] = cost, [removed]
            elif cost == out[k]:
                optimal[k].append(removed)
    return {'gamma': gamma, 'profile': out, 'optimal': optimal, 'admissible_cuts': count}
