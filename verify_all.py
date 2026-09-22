"""Verify all final certificates using the Python standard library only."""
import json
from itertools import combinations
from certificates import check,verify_coverage,verify_realizer,adjacencies

check()
verify_coverage()
rs=json.load(open('experiments.json'))
assert len(rs)==1092 and {r['n'] for r in rs}==set(range(3,13))
record_map={(r['n'],r['index']):r for r in rs}
parents={r['index']:r for r in rs if r['n']==10 and not r['test3']['feasible']}
dels=json.load(open('vertex_deletion_realizers.json'))
assert len(dels)==70
assert {(r['parent_index'],r['removed_vertex']) for r in dels}=={(i,v) for i in parents for v in range(10)}
for rec in dels:
    v=rec['removed_vertex'];parent=parents[rec['parent_index']]
    rem=[u for u in range(10) if u!=v];ix={u:i for i,u in enumerate(rem)}
    assert rec['remaining_labels']==rem
    E=[(ix[a],ix[b]) for a,b in parent['edges'] if a!=v and b!=v]
    assert E==list(map(tuple,rec['edges']))
    assert len(rec['orders'])==3 and verify_realizer(9,E,rec['orders'])
print('Verified all 70 single-vertex deletion certificates')

def dual(n,edges):
    adj=adjacencies(n,edges)
    ts=[set(t) for t in combinations(range(n),3) if all(v in adj[u] for u,v in combinations(t,2))]
    return len(ts),{(i,j) for i,j in combinations(range(len(ts)),2) if len(ts[i]&ts[j])==2}
w=json.load(open('weak_dual_counterexample.json'));a=w['dimension3_graph'];b=w['dimension4_graph']
for rec in (a,b):
    source=record_map[rec['n'],rec['index']]
    assert rec['edges']==source['edges'] and rec['test3']['feasible']==source['test3']['feasible']
assert a['test3']['feasible'] is True and b['test3']['feasible'] is False
na,da=dual(a['n'],a['edges']);nb,db=dual(b['n'],b['edges']);mp={int(k):v for k,v in w['dual_isomorphism'].items()}
assert na==nb and set(mp)==set(range(na)) and set(mp.values())==set(range(nb))
assert {tuple(sorted((mp[u],mp[v]))) for u,v in da}==db
assert verify_realizer(a['n'],a['edges'],a['test3']['orders'])
print('Verified the weak-dual counterexample')

for rec in json.load(open('implication_certificates.json')):
    source=record_map[rec['n'],rec['index']]
    assert rec['edges']==source['edges'] and rec['colors']==source['colors']
    paths=rec['paths']
    if paths is None:continue
    adj=adjacencies(rec['n'],rec['edges']);c=rec['colors']
    assert paths[0][0]==paths[1][-1] and paths[0][-1]==paths[1][0]
    assert paths[0][0]['pair']==paths[0][-1]['pair'] and paths[0][0]['color']!=paths[0][-1]['color']
    for seq in paths:
        for p in seq:
            u,v=p['pair'];assert v not in adj[u] and c[u]!=c[v] and p['color'] in {c[u],c[v]}
        for p,q in zip(seq,seq[1:]):
            u,v=p['pair'];x,y=q['pair']
            assert y in adj[u] and v in adj[x]
            assert p['color']!=q['color'] and {p['color'],q['color']}=={c[x],c[y]}
print('Verified all explicit implication chains')
ops=json.load(open('outerpath_realizers.json'))
expected=set()
for rec in rs:
    size,edges=dual(rec['n'],rec['edges']);degree=[0]*size
    for u,v in edges:degree[u]+=1;degree[v]+=1
    if max(degree,default=0)<=2:expected.add((rec['n'],rec['index']))
assert len(ops)==len(expected)==152
assert {(rec['n'],rec['index']) for rec in ops}==expected
for rec in ops:
    r=record_map[rec['n'],rec['index']]
    assert len(rec['orders'])==3 and verify_realizer(r['n'],r['edges'],rec['orders'])
print('Verified',len(ops),'constructive outerpath realizers')
print('ALL CERTIFICATE CHECKS PASSED')
