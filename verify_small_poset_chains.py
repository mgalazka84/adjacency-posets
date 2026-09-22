"""Exhaustive small-poset check of the constructive cocomparability theorem.

Run from the supplementary source directory containing constructions.py:
    python verify_small_poset_chains.py

Every finite poset admits a linear extension. Relabeling along that extension
puts every strict comparability into a pair u < v of integer labels. Enumerating
all transitive subsets of those pairs therefore covers all posets up to five
vertices, with repetitions between isomorphic posets. Every set partition is
then checked for being a partition into nonempty chains.

This is implementation validation; the mathematical proof establishes the
unbounded theorem. It makes no claim about bibliographic priority.
"""
from itertools import combinations

from constructions import chain_realizer
from certificates import verify_realizer


def partitions(n):
    def visit(v, blocks):
        if v == n:
            yield [b[:] for b in blocks]
            return
        for b in blocks:
            b.append(v)
            yield from visit(v + 1, blocks)
            b.pop()
        blocks.append([v])
        yield from visit(v + 1, blocks)
        blocks.pop()

    yield from visit(0, [])


posets = checked = 0
for n in range(1, 6):
    pairs = list(combinations(range(n), 2))
    parts = list(partitions(n))
    count = 0
    for mask in range(1 << len(pairs)):
        lt = [[False] * n for _ in range(n)]
        for p, (u, v) in enumerate(pairs):
            lt[u][v] = bool(mask & (1 << p))
        if any(lt[u][v] and lt[v][w] and not lt[u][w]
               for u, v, w in combinations(range(n), 3)):
            continue
        posets += 1
        edges = [(u, v) for u, v in pairs if not lt[u][v]]
        for chains in parts:
            if not all(lt[u][v] for chain in chains
                       for u, v in combinations(chain, 2)):
                continue
            orders = chain_realizer(lt, chains)
            assert len(orders) == max(2, len(chains))
            assert verify_realizer(n, edges, orders)
            checked += 1
            count += 1
    print('order', n, 'valid chain partitions checked', count)
print('PASS:', posets, 'naturally labeled posets;', checked,
      'chain partitions; all orders <=5')
