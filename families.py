"""Construct and verify the spider family S(4r+3, 2, 2)."""
import json
from pathlib import Path
from bondage import bondage_profile
from bruteforce import profile as oracle


def spider(r):
    if r < 1:
        raise ValueError('r must be positive')
    length = 4*r+3
    edges = [(i, i+1) for i in range(length)]
    edges += [(0, length+1), (length+1, length+2),
              (0, length+3), (length+3, length+4)]
    return length+5, edges


def formula(r):
    return list(range(2*r+2)) + [2*r+3, 2*r+3]


if __name__ == '__main__':
    records = []
    for r in range(1, 31):
        n, edges = spider(r)
        result = bondage_profile(n, edges)
        expected = formula(r)
        assert result['gamma'] == 2*r+5
        assert result['profile'] == expected
        # The two optimal single deletions are the short-arm inner edges.
        singles = {tuple(x) for x in oracle(n, edges)['optimal'][1]} if r == 1 else None
        if r == 1:
            assert singles == {(4*r+3,), (4*r+5,)}
        records.append({'r': r, 'n': n, 'gamma': result['gamma'],
                        'profile': expected, 'peak_states': result['peak_states']})
    Path('results').mkdir(exist_ok=True)
    Path('results/spider_family.json').write_text(json.dumps(records, indent=2)+'\n')
    print('Verified the closed profile formula for r=1,...,30 (orders 12,...,128).')
