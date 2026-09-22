from research import *
from collections import deque,Counter
from pysat.solvers import Solver

def conflict_graph(n,edges,all_critical=False):
    adj=adjacency(n,edges)
    pairs=[(u,v) for u in range(n) for v in range(n) if v not in adj[u]]
    cons=[(a,b) for a,b in combinations(range(len(pairs)),2)
          if pairs[b][1] in adj[pairs[a][0]] and pairs[a][1] in adj[pairs[b][0]]]
    if not all_critical:return pairs,cons
    # Generic critical pairs are ordered (x,y); a reversal puts y before x.
    pairs=[(u,n+v) for u,v in pairs]
    for u,v in ((u,v) for u in range(n) for v in range(n) if u!=v):
        if adj[v]<=adj[u]:pairs.append((u,v))
        if adj[u]<=adj[v]:pairs.append((n+u,n+v))
    def le(u,v):return u==v or (u<n<=v and v-n in adj[u])
    cons=[(a,b) for a,b in combinations(range(len(pairs)),2)
          if le(pairs[a][0],pairs[b][1]) and le(pairs[b][0],pairs[a][1])]
    return pairs,cons

def list_propagation(n,edges,color):
    pairs,cons=conflict_graph(n,edges);pindex={p:i for i,p in enumerate(pairs)}
    dom=[set(range(3)) for p in pairs];neigh=[set() for p in pairs]
    for a,b in cons:neigh[a].add(b);neigh[b].add(a)
    todo=deque();reasons={}
    for v in range(n):
        i=pindex[v,v];dom[i]={color[v]};todo.append(i)
        for c in range(3):
            if c!=color[v]:reasons[i,c]=('diagonal',v)
    steps=[]
    while todo:
        i=todo.popleft()
        if not dom[i]:return pairs,cons,dom,steps,i,reasons
        c=next(iter(dom[i]))
        for j in sorted(neigh[i]):
            if c in dom[j]:
                dom[j].remove(c);steps.append((j,c,i));reasons[j,c]=i
                if not dom[j]:return pairs,cons,dom,steps,j,reasons
                if len(dom[j])==1:todo.append(j)
    return pairs,cons,dom,steps,None,reasons

def conflict_colorable(n,edges,color=None,all_critical=False):
    pairs,cons=conflict_graph(n,edges,all_critical)
    clauses=[]
    for i in range(len(pairs)):
        clauses.append([3*i+c+1 for c in range(3)])
        for c,d in combinations(range(3),2):clauses.append([-3*i-c-1,-3*i-d-1])
    for a,b in cons:
        for c in range(3):clauses.append([-3*a-c-1,-3*b-c-1])
    if color is not None:
        for i,(u,v) in enumerate(pairs):
            if (u==v and not all_critical) or (all_critical and v==n+u):clauses.append([3*i+color[u]+1])
    with Solver(name='g4',bootstrap_with=clauses) as s:
        ok=s.solve()
    return ok

def shrink(n,edges):
    labels=list(range(n));E=list(map(tuple,edges));deleted=[]
    while True:
        for v in range(n):
            rem=[i for i in range(n) if i!=v];mapping={x:i for i,x in enumerate(rem)}
            EE=[(mapping[a],mapping[b]) for a,b in E if a!=v and b!=v]
            if not dimension_at_most(n-1,EE)['feasible']:
                deleted.append(labels[v]);labels=[labels[i] for i in rem];n-=1;E=EE
                break
        else:break
    return n,E,labels,deleted

if __name__=='__main__':
    records=json.load(open('experiments.json'));counts=Counter(); small=[]
    for rec in records:
        n=rec['n'];E=rec['edges'];c=rec['colors']
        if rec['test3']['feasible']:continue
        pairs,cons,dom,steps,bad,reasons=list_propagation(n,E,c)
        counts[n,'prop' if bad is not None else 'notprop']+=1
        if bad is None:
            col=conflict_colorable(n,E,c);counts[n,'conflictSAT' if col else 'conflictUNSAT']+=1
        if n==10:
            shr=shrink(n,E);small.append({'record':rec,'shrink':shr})
            print('SMALL',rec['index'],'prop',bad is not None,'shrink',shr,'cats',rec['caterpillars'],flush=True)
    print(counts,flush=True)
    json.dump(small,open('small_obstructions.json','w'),indent=2)
