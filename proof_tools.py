"""Small independently checkable lower-bound certificates."""
from research import *
from structural import conflict_graph
from collections import deque

def two_sat_paths(n,edges,color):
    pairs,cons=conflict_graph(n,edges)
    domains=[{color[u],color[v]} for u,v in pairs]
    arcs={}
    for a,b in cons:
        for c in domains[a]&domains[b]:
            if len(domains[a])==len(domains[b])==2:
                othera=next(iter(domains[a]-{c}));otherb=next(iter(domains[b]-{c}))
                arcs.setdefault((a,c),[]).append((b,otherb))
                arcs.setdefault((b,c),[]).append((a,othera))
    def path(s,t):
        todo=deque([s]);prev={s:None}
        while todo:
            u=todo.popleft()
            if u==t:
                out=[]
                while u is not None:out.append(u);u=prev[u]
                return out[::-1]
            for v in arcs.get(u,[]):
                if v not in prev:prev[v]=u;todo.append(v)
        return None
    best=None
    for a in range(len(pairs)):
        if len(domains[a])!=2:continue
        c,d=sorted(domains[a]);p=path((a,c),(a,d));q=path((a,d),(a,c))
        if p and q and (best is None or len(p)+len(q)<len(best[0])+len(best[1])):best=(p,q)
    if best:
        return [[{'pair':pairs[a],'color':c} for a,c in seq] for seq in best]
    return None

def verify_implication_paths(n,edges,color,paths):
    adj=adjacency(n,edges)
    if len(paths)!=2:return False
    if paths[0][0]!=paths[1][-1] or paths[0][-1]!=paths[1][0]:return False
    if paths[0][0]['pair']!=paths[0][-1]['pair'] or paths[0][0]['color']==paths[0][-1]['color']:return False
    for seq in paths:
        for p in seq:
            u,v=p['pair']
            if v in adj[u] or color[u]==color[v] or p['color'] not in [color[u],color[v]]:return False
        for x,y in zip(seq,seq[1:]):
            u,v=x['pair'];a,b=y['pair'];c=x['color'];d=y['color']
            if b not in adj[u] or v not in adj[a]:return False
            if c==d or {c,d}!={color[a],color[b]}:return False
    return True

if __name__=='__main__':
    records=json.load(open('experiments.json'));out=[]
    for r in [x for x in records if x['n']==10 and not x['test3']['feasible']]:
        p=two_sat_paths(r['n'],r['edges'],r['colors'])
        print(r['index'],p,flush=True)
        if p:assert verify_implication_paths(r['n'],r['edges'],r['colors'],p)
        out.append({'n':r['n'],'index':r['index'],'edges':r['edges'],'colors':r['colors'],'paths':p})
    json.dump(out,open('implication_certificates.json','w'),indent=2)
