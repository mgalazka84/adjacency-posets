"""Exact formulations and reproducible experiments for adjacency-poset dimension.

Vertices use 0,...,n-1; poset elements v- and v+ use v and n+v.
MILP infeasibility is a computational result, not a formal proof certificate.
All returned realizers are verified combinatorially, without floating point.
"""
from functools import lru_cache
from itertools import combinations
import json, time, sys

def adjacency(n, edges):
    out=[set() for _ in range(n)]
    for a,b in edges: out[a].add(b); out[b].add(a)
    return out

def three_coloring(n, edges):
    adj=adjacency(n,edges); color=[-1]*n
    def go():
        todo=[i for i in range(n) if color[i]<0]
        if not todo: return True
        v=max(todo,key=lambda x:(len({color[y] for y in adj[x] if color[y]>=0}),len(adj[x])))
        banned={color[y] for y in adj[v]}
        for c in range(3):
            if c not in banned:
                color[v]=c
                if go(): return True
        color[v]=-1
        return False
    if not go(): return None
    return color

def verify_realizer(n, edges, orders):
    N=2*n; adj=adjacency(n,edges)
    if any(sorted(L)!=list(range(N)) for L in orders): return False
    ranks=[{x:i for i,x in enumerate(L)} for L in orders]
    for a in range(N):
        for b in range(N):
            if a==b: continue
            comparable=a<n<=b and b-n in adj[a]
            if all(r[a]<r[b] for r in ranks)!=comparable: return False
    return True

def linear_order_cnf(n, edges, d=3, color=None, monochromatic_blocks=False):
    """Generic exact CNF; optional fixed diagonal colors require justification."""
    N=2*n; adj=adjacency(n,edges); ids={}; ctr=0
    for k in range(d):
        for a,b in combinations(range(N),2): ctr+=1; ids[k,a,b]=ctr
    def lit(k,a,b): return ids[k,a,b] if a<b else -ids[k,b,a]
    clauses=[]
    for k in range(d):
        for a,b,c in combinations(range(N),3):
            clauses.append([-lit(k,a,b),-lit(k,b,c),lit(k,a,c)])
            clauses.append([lit(k,a,b),lit(k,b,c),-lit(k,a,c)])
    for a,b in combinations(range(N),2):
        if a<n<=b and b-n in adj[a]:
            clauses.extend([[lit(k,a,b)] for k in range(d)])
        else:
            clauses.append([lit(k,a,b) for k in range(d)])
            clauses.append([-lit(k,a,b) for k in range(d)])
    if color is not None:
        for v in range(n):
            for k in range(d):
                clauses.append([lit(k,v,n+v)*(1 if color[v]!=k else -1)])
        if monochromatic_blocks:
            for u in range(n):
                for v in range(n):
                    if color[u]==color[v]: clauses.append([-lit(color[u],u,n+v)])
    return ctr,clauses,ids

def dimension_at_most_milp(n,edges,d=3,color=None,monochromatic_blocks=False,timeout=30):
    import numpy as np
    from scipy.optimize import milp, Bounds, LinearConstraint
    from scipy.sparse import coo_matrix
    nv,clauses,ids=linear_order_cnf(n,edges,d,color,monochromatic_blocks)
    # Map each CNF clause to sum(positive x)-sum(negative x)>=1-negatives.
    row=[];col=[];data=[];low=[]
    for i,cl in enumerate(clauses):
        neg=0
        for z in cl:
            row.append(i);col.append(abs(z)-1);data.append(1 if z>0 else -1)
            neg+=z<0
        low.append(1-neg)
    A=coo_matrix((data,(row,col)),shape=(len(clauses),nv)).tocsc()
    res=milp(np.zeros(nv),integrality=np.ones(nv),bounds=Bounds(0,1),
        constraints=LinearConstraint(A,np.array(low),np.inf),
        options={'time_limit':timeout,'mip_rel_gap':0})
    out={'status':int(res.status),'message':res.message}
    if res.x is not None:
        vals=np.rint(res.x).astype(int)
        if not all(any((vals[abs(z)-1]==1)==(z>0) for z in cl) for cl in clauses):
            raise RuntimeError('Solver output violates CNF')
        orders=[]
        for k in range(d):
            wins=[0]*(2*n)
            for a,b in combinations(range(2*n),2):
                if vals[ids[k,a,b]-1]: wins[b]+=1
                else: wins[a]+=1
            orders.append(sorted(range(2*n),key=lambda a:wins[a]))
        if not verify_realizer(n,edges,orders): raise RuntimeError('Invalid realizer')
        out['orders']=orders;out['feasible']=True
    elif res.status==2: out['feasible']=False
    else: out['feasible']=None
    return out

def dimension_at_most(n,edges,d=3,color=None,monochromatic_blocks=False,proof=False):
    from pysat.solvers import Solver
    nv,clauses,ids=linear_order_cnf(n,edges,d,color,monochromatic_blocks)
    with Solver(name='g4',bootstrap_with=clauses,with_proof=proof) as solver:
        feasible=solver.solve()
        out={'feasible':feasible,'solver':'Glucose4','variables':nv,'clauses':len(clauses)}
        if feasible:
            positive={x for x in solver.get_model() if x>0};orders=[]
            for k in range(d):
                wins=[0]*(2*n)
                for a,b in combinations(range(2*n),2):
                    if ids[k,a,b] in positive:wins[b]+=1
                    else:wins[a]+=1
                orders.append(sorted(range(2*n),key=lambda a:wins[a]))
            if not verify_realizer(n,edges,orders):raise RuntimeError('SAT realizer failed verification')
            out['orders']=orders
        elif proof:out['proof']=solver.get_proof()
    return out

@lru_cache(None)
def triangulations(vertices):
    if len(vertices)<3: return (frozenset(),)
    a,b=vertices[0],vertices[-1]; out=[]
    for j in range(1,len(vertices)-1):
        c=vertices[j]; tri=frozenset({tuple(sorted((a,c))),tuple(sorted((b,c))),tuple(sorted((a,b)))})
        for L in triangulations(vertices[:j+1]):
            for R in triangulations(vertices[j:]): out.append(L|R|tri)
    return tuple(out)

def canonical_polygon(n,edges):
    return min(tuple(sorted(tuple(sorted(((s*a+t)%n,(s*b+t)%n))) for a,b in edges))
        for s in [-1,1] for t in range(n))

def mops(n):
    return sorted({canonical_polygon(n,e) for e in triangulations(tuple(range(n)))})

def weak_dual(n,edges):
    adj=adjacency(n,edges)
    triangles=[set(t) for t in combinations(range(n),3) if all(v in adj[u] for u,v in combinations(t,2))]
    return [(i,j) for i,j in combinations(range(len(triangles)),2) if len(triangles[i]&triangles[j])==2]

def bichromatic_caterpillars(n,edges,color):
    ans=[]
    for a,b in combinations(range(3),2):
        nodes={v for v in range(n) if color[v] in (a,b)}
        adj=adjacency(n,[(u,v) for u,v in edges if u in nodes and v in nodes])
        core={v for v in nodes if len(adj[v])>=2}
        ans.append(all(len(adj[v]&core)<=2 for v in core))
    return ans

def run(maxn=10):
    records=[]
    for n in range(3,maxn+1):
        graphs=mops(n); counts={}; start=time.time()
        for j,e in enumerate(graphs):
            c=three_coloring(n,e); cats=bichromatic_caterpillars(n,e,c)
            result=dimension_at_most(n,e,color=c)
            rec={'n':n,'index':j,'edges':e,'colors':c,'caterpillars':cats,
                'weak_dual_edges':weak_dual(n,e),'test3':result}
            records.append(rec)
            key=str(result['feasible']);counts[key]=counts.get(key,0)+1
            if result['feasible'] is False and counts[key]<=3: print('DIM4',n,j,e,flush=True)
        with open('experiments.json','w') as f:json.dump(records,f,indent=2)
        print('DONE',n,len(graphs),counts,round(time.time()-start,2),flush=True)
    return records

if __name__=='__main__': run(int(sys.argv[1]) if len(sys.argv)>1 else 10)
