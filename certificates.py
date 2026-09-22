"""Integer-only certificates. This module uses only the Python standard library.

An UNSAT tree certifies that necessary reversal-color constraints have no solution.
It does not claim that these constraints characterize dimension three in general.
"""
from itertools import combinations
import json

def adjacencies(n,edges):
    adj=[set() for _ in range(n)]
    for a,b in edges:adj[a].add(b);adj[b].add(a)
    return adj

def is_mop(n,edges):
    E={tuple(sorted(e)) for e in edges}
    if n<3 or len(E)!=2*n-3:return False
    if not all(tuple(sorted((i,(i+1)%n))) in E for i in range(n)):return False
    for (a,b),(c,d) in combinations(E,2):
        if a<c<b<d or c<a<d<b:return False
    return True

def verify_realizer(n,edges,orders):
    adj=adjacencies(n,edges);N=2*n
    if not orders or any(sorted(L)!=list(range(N)) for L in orders):return False
    ranks=[{v:i for i,v in enumerate(L)} for L in orders]
    return all(all(r[x]<r[y] for r in ranks)==(x<n<=y and y-n in adj[x])
        for x in range(N) for y in range(N) if x!=y)

def critical_constraints(n,edges,color):
    """All ordered critical pairs, exact 2-cycle conflicts, rigidity-based lists."""
    adj=adjacencies(n,edges)
    assert len(color)==n and set(color)=={0,1,2}
    assert all(color[a]!=color[b] for a,b in edges)
    pairs=[(u,n+v) for u in range(n) for v in range(n) if v not in adj[u]]
    domains=[(1<<color[u]) | (1<<color[v]) for u in range(n) for v in range(n) if v not in adj[u]]
    for u in range(n):
        for v in range(n):
            if u==v:continue
            if adj[v]<=adj[u]:pairs.append((u,v));domains.append(7)
            if adj[u]<=adj[v]:pairs.append((n+u,n+v));domains.append(7)
    def le(u,v):return u==v or (u<n<=v and v-n in adj[u])
    neighbors=[set() for p in pairs]
    for a,b in combinations(range(len(pairs)),2):
        if le(pairs[a][0],pairs[b][1]) and le(pairs[b][0],pairs[a][1]):
            neighbors[a].add(b);neighbors[b].add(a)
    return pairs,neighbors,domains

def propagate(domains,neighbors):
    domains=domains[:];todo=[i for i,d in enumerate(domains) if d and d&(d-1)==0]
    done=set()
    while todo:
        v=todo.pop()
        if v in done:continue
        done.add(v);d=domains[v]
        if d==0:return None
        for w in sorted(neighbors[v]):
            if domains[w]&d:
                domains[w]&=~d
                if not domains[w]:return None
                if domains[w]&(domains[w]-1)==0:todo.append(w)
    return domains

def unsat_tree(domains,neighbors):
    ds=propagate(domains,neighbors)
    if ds is None:return {'conflict':True}
    todo=[i for i,d in enumerate(ds) if d.bit_count()>1]
    if not todo:raise ValueError('Necessary constraints are satisfiable')
    v=min(todo,key=lambda i:(ds[i].bit_count(),-sum(ds[j].bit_count()>1 for j in neighbors[i]),i))
    children={}
    for c in range(3):
        if ds[v]&(1<<c):
            dd=ds[:];dd[v]=1<<c
            children[str(c)]=unsat_tree(dd,neighbors)
    return {'pair_index':v,'branches':children}

def check_unsat_tree(domains,neighbors,tree):
    ds=propagate(domains,neighbors)
    if ds is None:return tree=={'conflict':True}
    if set(tree)!={'pair_index','branches'}:return False
    v=tree['pair_index']
    if not isinstance(v,int) or not 0<=v<len(ds):return False
    choices={str(c) for c in range(3) if ds[v]&(1<<c)}
    if len(choices)<2 or set(tree['branches'])!=choices:return False
    for c in choices:
        dd=ds[:];dd[v]=1<<int(c)
        if not check_unsat_tree(dd,neighbors,tree['branches'][c]):return False
    return True

def tree_size(tree):
    return 1+sum(tree_size(t) for t in tree.get('branches',{}).values())

def produce():
    records=json.load(open('experiments.json'));certs=[]
    for r in records:
        if r['test3']['feasible']:continue
        pairs,neigh,domains=critical_constraints(r['n'],r['edges'],r['colors'])
        tree=unsat_tree(domains,neigh)
        assert check_unsat_tree(domains,neigh,tree)
        certs.append({'n':r['n'],'index':r['index'],'tree':tree,'nodes':tree_size(tree)})
        if r['n']==10:print('certificate',r['index'],'nodes',tree_size(tree),flush=True)
    json.dump(certs,open('negative_certificates.json','w'),indent=2)
    print('negative certificates',len(certs),'max nodes',max(x['nodes'] for x in certs))

def check():
    records=json.load(open('experiments.json'));certs={(r['n'],r['index']):r for r in json.load(open('negative_certificates.json'))}
    assert set(certs)=={(r['n'],r['index']) for r in records if r['test3']['feasible'] is False}
    counts={};seen=set()
    for r in records:
        n=r['n'];E=r['edges'];key=n,r['index']
        assert key not in seen;seen.add(key)
        assert is_mop(n,E)
        assert r['test3']['feasible'] is True or r['test3']['feasible'] is False
        if r['test3']['feasible']:
            assert len(r['test3']['orders'])==3 and verify_realizer(n,E,r['test3']['orders'])
            d=3
        else:
            pairs,neigh,domains=critical_constraints(n,E,r['colors'])
            assert check_unsat_tree(domains,neigh,certs[key]['tree'])
            d=4
        counts[n,d]=counts.get((n,d),0)+1
    print('Verified',len(records),'graphs;',len(certs),'lower-bound certificates;',counts)

def polygon_key(n,edges):
    """Canonical form under rotations/reflections of the unique outer cycle."""
    return min(tuple(sorted(tuple(sorted(((s*u+t)%n,(s*v+t)%n))) for u,v in edges))
        for s in (-1,1) for t in range(n))

def verify_coverage():
    """Independent ear-insertion generation, compared with Catalan-generated data."""
    records=json.load(open('experiments.json'));last={((0,1),(0,2),(1,2))}
    for n in range(3,max(r['n'] for r in records)+1):
        if n>3:
            new=set();m=n-1
            for E in last:
                for a in range(m):
                    insert=a+1
                    shift=lambda v:v+(v>=insert)
                    EE=[(shift(u),shift(v)) for u,v in E]
                    EE.extend([(shift(a),insert),(insert,shift((a+1)%m))])
                    new.add(polygon_key(n,EE))
            last=new
        actual={tuple(map(tuple,r['edges'])) for r in records if r['n']==n}
        assert len(actual)==len([r for r in records if r['n']==n])
        assert actual==last
        print('Coverage',n,len(last),'OK',flush=True)

if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='produce':produce()
    elif len(sys.argv)>1 and sys.argv[1]=='coverage':verify_coverage()
    else:check()
