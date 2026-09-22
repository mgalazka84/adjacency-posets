"""Regenerate auxiliary certificates from the complete experiment list.

Requires the SAT discovery dependency in requirements-search.txt.
The resulting files are checked independently by verify_all.py.
"""
import json
from itertools import combinations, permutations
from research import dimension_at_most, adjacency

records = json.load(open('experiments.json'))
parents = [r for r in records if r['n'] == 10 and not r['test3']['feasible']]
deletions = []
for parent in parents:
    for v in range(10):
        rem = [u for u in range(10) if u != v]
        index = {u: i for i, u in enumerate(rem)}
        edges = [(index[a], index[b]) for a, b in parent['edges'] if a != v and b != v]
        result = dimension_at_most(9, edges)
        assert result['feasible']
        deletions.append({'parent_index': parent['index'], 'removed_vertex': v,
                          'remaining_labels': rem, 'edges': edges, 'orders': result['orders']})
json.dump(deletions, open('vertex_deletion_realizers.json', 'w'), indent=2)

def dual(record):
    adj = adjacency(record['n'], record['edges'])
    triangles = [set(t) for t in combinations(range(record['n']), 3)
                 if all(v in adj[u] for u, v in combinations(t, 2))]
    edges = {(i, j) for i, j in combinations(range(len(triangles)), 2)
             if len(triangles[i] & triangles[j]) == 2}
    return len(triangles), edges

negative = next(r for r in records if (r['n'], r['index']) == (10, 19))
positive = next(r for r in records if (r['n'], r['index']) == (10, 20))
n, e = dual(positive)
m, f = dual(negative)
assert n == m
mapping = next(p for p in permutations(range(n))
               if {tuple(sorted((p[u], p[v]))) for u, v in e} == f)
json.dump({'dimension3_graph': positive, 'dimension4_graph': negative,
           'dual_isomorphism': dict(enumerate(mapping))},
          open('weak_dual_counterexample.json', 'w'), indent=2)
print('Regenerated 70 deletion certificates and the weak-dual counterexample')
