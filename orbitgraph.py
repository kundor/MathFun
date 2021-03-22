import igraph
from itertools import combinations, product

def rankfollow(G, v, rankseq):
    """Follow the edges of given ranks in order from v, returning the vertex reached"""
    if isinstance(v, igraph.Vertex):
        v = v.index
    for rank in rankseq:
        e = G.es.find(rank=rank, _between=([v], G.vs))
        a, b = e.tuple # vertices on the edge
        if a == v:
            v = b
        else:
            v = a
    return v

def pathlength(G, v, rankseq):
    """How many steps to return to v, when following edges with the given ranks in order?"""
    numsteps = 0
    w = v.index
    while True:
        w = rankfollow(G, w, rankseq)
        numsteps += 1
        if w == v.index:
            break
    return numsteps

def isfullrank(G):
    """Are all vertices incident to one edge of each rank?"""
    maxrank = max(G.es["rank"])
    D = maxrank + 1
    ranks = set(range(D))
    for v in G.vs:
        edges = set(G.incident(v))
        if len(edges) != D:
            return False
        if set(G.es[e]["rank"] for e in edges) != ranks:
            return False
    return True

def twocommute(G):
    """
    Do all edges of ranks differing by at least two "commute", in the sense
    that following alternating paths returns to the beginning in two steps?
    """
    D = max(G.es["rank"]) + 1
    for i in range(D - 2):
        for j in range(i+2, D):
            # we could do
            # K = G.es(rank_in = [i, j]).subgraph()
            # for each connected component: check if one of five possibilities
            # one vert with two loops, i-edge with two j-loops, j-edge with two i-loops, i&j double edge, or a four-cycle
            for v in G.vs:
                if v.index != rankfollow(G, v, (i, j, i, j)):
                    return False
    return True

def intransitive(G):
    """
    Does deleting edges of at least one rank leave G disconnected?
    Otherwise G is transitive on faces of each rank, hence the polytope is regular.
    """
    D = max(G.es["rank"]) + 1
    for k in range(D):
        K = G.es(rank_ne = k).subgraph(delete_vertices=False)
        if len(K.components()) > 1:
            return True
    return False

def noadjrankseven(G):
    """
    If at any vertex v it takes evenly many steps alternating i,i+1 edges to return,
    and evenly many steps alternating i-1,i edges, then G cannot be convex.
    """
    #Actually, one or the other (or both) must take 1 or 3 steps
    D = max(G.es["rank"]) + 1
    oldeven = False
    for i in range(1, D):
        alleven = True
        for v in G.vs:
            numsteps = pathlength(G, v, (i-1,i))
            if numsteps in (1, 3):
                alleven = False
                break
        if oldeven and alleven:
            return False
        oldeven = alleven
    return True

def isvalidorbit(G):
    """Is G an orbit graph for a convex polytope?"""
    return G.is_connected() and isfullrank(G) and twocommute(G) and (G.vcount() == 1 or intransitive(G)) and noadjrankseven(G)

def addloops(G, dim):
    """Add any missing loops to make G a dim-dimensional orbit graph."""
    ranks = set(range(dim))
    for v in G.vs:
        for rank in ranks - set(G.es[e]["rank"] for e in G.incident(v)):
            G.add_edge(v, v, rank=rank)

def oneorbit(dim):
    """One-vertex orbit graph for a regular polytope of given dimension"""
    return igraph.Graph(1, [(0,0)]*dim, edge_attrs={'rank': range(dim)})

def twoorbit(dim, intrans):
    """
    Two-orbit j-intransitive graph, transitive on all ranks except the given one.
    This can only be convex if intrans is 0 or dim-1, and dim is 2 or 3.
    """
    if intrans < 0 or intrans > dim - 1:
            raise ValueError("intrans must be an integer between 0 and dim - 1.")
    loops = [k for k in range(dim) if k != intrans]
    return igraph.Graph(2, [(0,0)]*(dim-1) + [(1,1)]*(dim-1) + [(0,1)], edge_attrs={'rank': loops*2 + [intrans]})

def threeorbitstring(dim, i):
    """
    Return a three-orbit graph with edges i and i+1 (type 3^{i,i+1}).
    This is only convex if i is 0 or dim-2 (and 2 <= dim <= 8).
    """
    # There cannot be i and j edges from the same vertex to distinct neighbors with |i-j| > 1,
    # since then there would have to be a fourth node
    if i < 0 or i > dim - 2:
        raise ValueError("i must be an integer between 0 and dim - 2.")
    return igraph.Graph(3, [(0,0)]*(dim-1) + [(1,1)]*(dim-2) + [(2,2)]*(dim-1) + [(0,1), (1,2)],
                edge_attrs={'rank': [k for k in range(dim) if k != i] +
                                    [k for k in range(dim) if k not in (i, i+1)] + 
                                    [k for k in range(dim) if k != i+1] + 
                                    [i, i+1]})

def threeorbitmulti(dim, i):
    """
    Return a three-orbit graph with one i-edge, and then a double i+1, i-1 edge (type 3^i).
    This can only be convex if i is 1 or dim-2 (and 3 <= dim <= 6).
    """
    if i < 1 or i > dim - 2:
        raise ValueError("i must be an integer between 1 and dim - 2.")
    return igraph.Graph(3, [(0,0)]*(dim-1) + [(1,1)]*(dim-3) + [(2,2)]*(dim-2) + [(0,1), (1,2), (1,2)],
                edge_attrs={'rank': [k for k in range(dim) if k != i] +
                                    [k for k in range(dim) if k not in (i-1, i, i+1)] + 
                                    [k for k in range(dim) if k not in (i-1, i+1)] + 
                                    [i, i-1, i+1]})

def isomorphicorbits(G, K):
    """Are G and K isomorphic (respecting edge ranks)?"""
    if G.ecount() != K.ecount():
        return False
    return G.isomorphic_vf2(K, edge_color1=G.es['rank'], edge_color2=K.es['rank']) 

def covers(G, K):
    """Does G cover K as an orbit graph? (Thesis, II.5)"""
    ng = G.vcount()
    nk = K.vcount()
    if ng == nk:
        return isomorphicorbits(G, K)
    if ng < nk:
        return False
    if ng % nk:
        return False
    D = max(G.es["rank"]) + 1
    if D != max(K.es["rank"]) + 1:
        return False
    if nk == 1:
        return True
    raise NotImplementedError('Whoops')

def _poss_edge_sets(verts):
    """Recursively lists possible non-incident edges among the given vertices.
       Internal for poss_edge_sets."""
    curedges = [[]]
    for pair in combinations(verts, 2):
        remverts = verts - set(pair)
        for edges in _poss_edge_sets(remverts):
            curedges.append([pair] + edges)
    return curedges

def poss_edge_sets(numorbit):
    """All possible sets of non-incident edges among numorbit vertices."""
    allsets = _poss_edge_sets(set(range(numorbit)))
    poss_rank_edges = []
    for es in allsets:
        if sorted(es) in poss_rank_edges:
            continue
        poss_rank_edges.append(es)
    return poss_rank_edges

def isomorphism_representatives(graphs, class_sizes = False):
    """Given a list of orbit graphs, return one from each isomorphism class, and optionally the class sizes"""
    isom_class_reps = []
    isom_class_nums = []
    for g in graphs:
        for i,k in enumerate(isom_class_reps):
            if isomorphicorbits(g, k):
                isom_class_nums[i] += 1
                break
        else:
            isom_class_reps.append(g)
            isom_class_nums.append(1)
    if class_sizes:
        return isom_class_reps, isom_class_nums
    return isom_class_reps

def _orbit_graphs(numorbit, dim, convex=True):
    """Generates all possible orbit graphs, throws out the bad ones, and finds isomorphism representatives."""
    possible_irank_edgesets = poss_edge_sets(numorbit)
    all_graphs = []
    for rankedges in product(possible_irank_edgesets, repeat=dim):
        edgeranks = []
        for rank, edges in enumerate(rankedges):
            edgeranks += [rank] * len(edges)
        graph_edges = sum(rankedges, [])
        G = igraph.Graph(numorbit, graph_edges, edge_attrs={'rank': edgeranks})
        addloops(G, dim)
        all_graphs.append(G)
    if convex:
        ok_graphs = [g for g in all_graphs if isvalidorbit(g)]
    else:
        ok_graphs = [g for g in all_graphs if g.is_connected() and twocommute(g)]
    # (FIXME) actually adj_ranks_even applies also for tilings if dim != 3
    # also probably a more subtle version of intransitivity applies
    # (the full tiling could be fully-transitive, but each face and vertex figure
    # must not be)
    return isomorphism_representatives(ok_graphs)

def orbitgraphs(numorbits, dim, convex=True):
    """Return a list of all valid k-orbit graphs for d-dimensional convex polytopes."""
    if numorbits < 1 or dim < 0 or (dim < 1 and numorbits > 1) or (dim < 2 and numorbits > 2):
        return []
    if numorbits == 1:
        return [oneorbit(dim)]
    if numorbits == 2 and convex:
        if dim > 1:
            return [twoorbit(dim, 0), twoorbit(dim, dim-1)]
        return [twoorbit(dim, 0)]
        # no convex two-orbit polytopes exist except in dimensions two or three
        # but the orbit graphs are valid...and could appear as subgraphs
    if numorbits == 3 and convex:
        return [threeorbitstring(dim, i) for i in range(dim-1)] + [threeorbitmulti(dim, i) for i in range(1, dim-1)]
        # string type can only be convex if i is 0 or dim-2, but the rest are valid as graphs
        # the other type can only be convex if i is 1 or dim - 2
    return _orbit_graphs(numorbits, dim, convex)

def dual(G):
    """Return the dual orbit graph to G"""
    K = G.copy()
    maxrank = max(K.es["rank"])
    K.es.set_attribute_values('rank', [maxrank-r for r in K.es["rank"]])
    return K

def restrictions(G, l, j):
    """Returns all the restricted graphs for sections of an l-face over a j-face;
    see Thesis III.2."""
    if j >= l:
        return []
    sections = []
    G_jl = G.es(rank_notin=(j, l)).subgraph()
    for X in G_jl.components().subgraphs():
        K = X.es(rank_in=range(j+1,l)).subgraph()
        kcomps = K.components().subgraphs()
        K0 = kcomps[0]
        if any(not K0.isomorphic(kc) for kc in kcomps[1:]):
            raise ValueError('Thesis is wrong?')
        K0.es.set_attribute_values('rank', [r - j - 1 for r in K0.es["rank"]])
        sections.append(K0)
    return sections
    # Just returning components after removing all edges with rank at most j or at least l is redundant
    # we should first find the components of G_jl, removing only j-edges and l-edges
    # each component of K is contained in one of these components; 
    # if there are multiple components of K in a component of G_jl,
    # they are all isomorphic (Lemma II.2.1) and only one should be included

def contractions(G, l, j):
    """Return all the contracted graphs for sections of an l-face over a j-face"""
    if j >= l:
        return []
    sections = []
    G_jl = G.es(rank_notin=(j,l)).subgraph()
    for X in G_jl.components().subgraphs():
        clusters = X.es(rank_notin=range(j+1,l)).subgraph(delete_vertices=False).components()
        X.contract_vertices(clusters.membership)
        X.delete_edges(rank_notin=range(j+1,l))
        X.es.set_attribute_values('rank', [r - j - 1 for r in X.es["rank"]])
        # wherever there are multiple edges with the same rank between two nodes, replace them with a single edge
        edgetodel = []
        vertsrank = set()
        for e in X.es:
            vsrk = min(e.tuple), max(e.tuple), e["rank"]
            if vsrk in vertsrank:
                edgetodel += [e.index]
            else:
                vertsrank.add(vsrk)
        X.delete_edges(edgetodel)
        sections.append(X)
    return sections

def showedges(G):
    print('\n'.join(str((e.tuple, e['rank'])) for e in G.es))

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        sys.exit('Two arguments: dimension and number of orbits')
    dim = int(sys.argv[1])
    numorbit = int(sys.argv[2])
    for G in orbitgraphs(numorbit, dim, False):
        showedges(G)
        print()

