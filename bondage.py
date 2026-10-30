"""Exact weighted total-bondage profiles of trees.

The core solver uses only the Python standard library. Vertices are 0,...,n-1.
A signature has entries (out/relaxed, out/required, in/relaxed, in/required).
Only deletion sets leaving no isolated vertex are accepted at the root.
"""
from dataclasses import dataclass
from math import inf
from numbers import Rational


def keep(left, right):
    """Retain the edge joining the two roots; retain the left root."""
    return tuple(min(left[2*a + b*(1-c)] + right[2*c + 1-a]
                     for c in (0, 1))
                 for a in (0, 1) for b in (0, 1))


def cut(left, right):
    """Delete the joining edge; the right root must be dominated internally."""
    t = min(right[1], right[3])
    return tuple(x + t for x in left)


@dataclass(frozen=True, slots=True)
class Trace:
    left: object
    right: object
    edge: object = None


def trace_edges(trace):
    out, stack = [], [trace]
    while stack:
        t = stack.pop()
        if t is None:
            continue
        if t.edge is not None:
            out.append(t.edge)
        stack.extend((t.left, t.right))
    return tuple(sorted(out))


def _join_trace(left, right, edge):
    if edge is None:
        if left is None:
            return right
        if right is None:
            return left
    return Trace(left, right, edge)


def _rooted(n, edges, root):
    if not isinstance(n, int) or n < 2:
        raise ValueError('A tree must have at least two vertices.')
    if root not in range(n) or len(edges) != n - 1:
        raise ValueError('Invalid root or edge count.')
    adjacency = [[] for _ in range(n)]
    seen_edges = set()
    for i, (u, v) in enumerate(edges):
        if u not in range(n) or v not in range(n) or u == v:
            raise ValueError('Invalid edge.')
        e = tuple(sorted((u, v)))
        if e in seen_edges:
            raise ValueError('Repeated edge.')
        seen_edges.add(e)
        adjacency[u].append((v, i))
        adjacency[v].append((u, i))
    parent = [-2] * n
    parent[root] = -1
    order = [root]
    children = [[] for _ in range(n)]
    for u in order:
        for v, i in adjacency[u]:
            if v == parent[u]:
                continue
            if parent[v] != -2:
                raise ValueError('Input is not a tree.')
            parent[v] = u
            children[u].append((v, i))
            order.append(v)
    if len(order) != n:
        raise ValueError('Input is disconnected.')
    return order, children


def total_domination_tree(n, edges, root=0):
    """Total domination number of a tree in linear time (four states)."""
    edges = list(edges)
    order, children = _rooted(n, edges, root)
    tables = {}
    for u in reversed(order):
        state = (0, inf, 1, inf)
        for v, _ in children[u]:
            state = keep(state, tables.pop(v))
        tables[u] = state
    return min(tables[root][1], tables[root][3])


def bondage_profile(n, edges, costs=None, root=0, witnesses=True):
    """Return all minimum deletion costs for increases k=0,...,n-gamma.

    Costs must be nonnegative rational numbers (ints or fractions.Fraction).
    A missing cost vector means unit costs. Infinity denotes an unattainable
    increase. Witnesses contain indices into the supplied edge sequence.

    The implementation uses sparse dictionaries; the O(n^4) deterministic
    arithmetic-operation bound uses the direct-address representation described
    in the accompanying research draft. Expected constant-time hash lookup
    yields the corresponding bound for this sparse implementation.
    """
    edges = [tuple(e) for e in edges]
    order, children = _rooted(n, edges, root)
    costs = [1] * len(edges) if costs is None else list(costs)
    if len(costs) != len(edges) or any(
        not isinstance(c, Rational) or c < 0 for c in costs
    ):
        raise ValueError('Provide one nonnegative rational cost per edge.')
    tables = {}
    peak_states = 1
    candidate_pairs = 0
    stored_states = 0
    for u in reversed(order):
        table = {(0, inf, 1, inf): (0, None)}
        for v, i in children[u]:
            child = tables.pop(v)
            new = {}
            candidate_pairs += len(table) * len(child)
            for left, (cl, tl) in table.items():
                for right, (cr, tr) in child.items():
                    for state, extra, deleted in (
                        (keep(left, right), 0, None),
                        (cut(left, right), costs[i], i),
                    ):
                        if all(x == inf for x in state):
                            continue
                        value = cl + cr + extra
                        if state not in new or value < new[state][0]:
                            trace = _join_trace(tl, tr, deleted) if witnesses else None
                            new[state] = value, trace
            table = new
            peak_states = max(peak_states, len(table))
            stored_states += len(table)
        tables[u] = table
    gamma = total_domination_tree(n, edges, root)
    best = [inf] * (n + 1)
    traces = [None] * (n + 1)
    for state, (value, trace) in tables[root].items():
        g = min(state[1], state[3])
        if g != inf and value < best[g]:
            best[g], traces[g] = value, trace
    for g in range(n - 1, -1, -1):
        if best[g + 1] < best[g]:
            best[g], traces[g] = best[g + 1], traces[g + 1]
    profile = best[gamma:]
    cuts = [trace_edges(t) if value != inf else None
            for value, t in zip(profile, traces[gamma:])] if witnesses else None
    return {'gamma': gamma, 'profile': profile, 'cuts': cuts,
            'peak_states': peak_states, 'candidate_pairs': candidate_pairs,
            'stored_states': stored_states}


if __name__ == '__main__':
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--path', type=int, default=8)
    args = parser.parse_args()
    result = bondage_profile(args.path, [(i, i+1) for i in range(args.path-1)])
    result['profile'] = [None if x == inf else x for x in result['profile']]
    print(json.dumps(result, indent=2))
