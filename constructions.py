"""Constructive upper bounds, independent of a SAT solver."""
from itertools import combinations
from certificates import verify_realizer

def chain_realizer(lt,chains):
    """Adjacency poset of the incomparability graph of a finite poset.

    lt[u][v] records strict order. chains partition its elements and are increasing.
    Return max(2, number of chains) linear extensions (nonempty posets).
    """
    n=len(lt);assert n>0
    assert sorted(v for C in chains for v in C)==list(range(n))
    for C in chains:
        assert all(lt[a][b] for a,b in zip(C,C[1:]))
    if len(chains)==1:
        return [list(range(2*n)),list(reversed(range(2*n)))]
    # A deterministic linear extension, used only to resolve tied slots.
    indeg=[sum(bool(lt[u][v]) for u in range(n)) for v in range(n)]
    extension=[];todo=[v for v in range(n) if not indeg[v]]
    while todo:
        v=min(todo);todo.remove(v);extension.append(v)
        for w in range(n):
            if lt[v][w]:
                indeg[w]-=1
                if not indeg[w]:todo.append(w)
    assert len(extension)==n
    rank={v:i for i,v in enumerate(extension)};orders=[]
    for C in chains:
        member=set(C);slots={i:[] for i in range(len(C)+1)}
        for v in range(n):
            if v in member:continue
            t=max([j for j,c in enumerate(C,1) if not lt[v][c]]+[0])
            slots[t].append(v)
        first=[]
        for j in range(len(C),0,-1):
            first.extend(sorted(slots[j],key=lambda v:-rank[v]))
            first.append(n+C[j-1])
        first.extend(sorted(slots[0],key=lambda v:-rank[v]))
        dual=lambda x:x+n if x<n else x-n
        orders.append(first+[dual(x) for x in reversed(first)])
    E=[(u,v) for u,v in combinations(range(n),2) if not lt[u][v] and not lt[v][u]]
    assert verify_realizer(n,E,orders)
    return orders

def interval_realizer(intervals):
    n=len(intervals)
    lt=[[intervals[u][1]<intervals[v][0] for v in range(n)] for u in range(n)]
    chains=[]
    for v in sorted(range(n),key=lambda u:(intervals[u][0],intervals[u][1],u)):
        for C in chains:
            if intervals[C[-1]][1]<intervals[v][0]:C.append(v);break
        else:chains.append([v])
    return chain_realizer(lt,chains),chains

def outerpath_intervals(n,edges):
    E={tuple(sorted(e)) for e in edges}
    tris=[t for t in combinations(range(n),3) if all((u,v) in E for u,v in combinations(t,2))]
    dual=[[] for _ in tris]
    for i,j in combinations(range(len(tris)),2):
        if len(set(tris[i])&set(tris[j]))==2:dual[i].append(j);dual[j].append(i)
    if any(len(a)>2 for a in dual):raise ValueError('The weak dual is not a path')
    current=next(i for i,a in enumerate(dual) if len(a)<=1);walk=[];prev=None
    while current is not None:
        walk.append(current);nxt=next((j for j in dual[current] if j!=prev),None)
        prev,current=current,nxt
    assert len(walk)==len(tris)
    positions={v:[] for v in range(n)}
    for i,t in enumerate(walk):
        for v in tris[t]:positions[v].append(i)
    intervals=[(min(positions[v]),max(positions[v])) for v in range(n)]
    actual={(u,v) for u,v in combinations(range(n),2) if max(intervals[u][0],intervals[v][0])<=min(intervals[u][1],intervals[v][1])}
    assert actual==E
    return intervals

if __name__=='__main__':
    import json,random
    r=random.Random(4701)
    for n in range(1,26):
        for _ in range(10):
            intervals=[tuple(sorted(r.sample(range(100),2))) for v in range(n)]
            interval_realizer(intervals)
    records=json.load(open('experiments.json'));checked=0;examples=[]
    for rec in records:
        try:intervals=outerpath_intervals(rec['n'],rec['edges'])
        except ValueError:continue
        orders,chains=interval_realizer(intervals)
        assert len(orders)==3
        examples.append({'n':rec['n'],'index':rec['index'],'intervals':intervals,'chains':chains,'orders':orders})
        checked+=1
    json.dump(examples,open('outerpath_realizers.json','w'),indent=2)
    print('Verified interval construction on 250 random instances and',checked,'enumerated outerpaths')
