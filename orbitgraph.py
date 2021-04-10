import igraph
from itertools import combinations, product
from colorama import Style

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

def is_rank(G, rank):
    """Are all vertices incident to one edge of each rank?"""
    D = rank + 1
    ranks = set(range(D))
    for v in G.vs:
        edges = set(G.incident(v))
        if len(edges) != D:
            return False
        if set(G.es[e]["rank"] for e in edges) != ranks:
            return False
    return True

def rank_deleted_components(G, ranks):
    """Return the connected components of G after removing all edges with labels in ranks"""
    K = G.es(rank_notin=ranks).subgraph(delete_vertices=False)
    return K.components().subgraphs()

def is_full_rank(G):
    """Are all vertices incident to one edge of the same ranks?"""
    maxrank = max(G.es["rank"])
    return is_rank(G, maxrank)

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
        if len(rank_deleted_components(G, {k})) > 1:
            return True
    return False

def is_even(G, i):
    """Is every (i,i+1)-walk even?"""
    return all(pathlength(G, v, (i,i+1)) % 2 == 0 for v in G.vs)

def is_not3(G, i):
    """Is every (i,i+1)-walk either even or greater than 4?"""
    return all(pathlength(G, v, (i,i+1)) not in (1,3) for v in G.vs)

def noadjranksnot3(G):
    """
    If at any vertex v it takes evenly many steps alternating i,i+1 edges to return,
    and evenly many steps alternating i-1,i edges, then G cannot be convex.
    In fact, one or the other (or both) must take 1 or 3 steps.
    """
    D = max(G.es["rank"])
    oldeven = False
    for i in range(D):
        alleven = is_not3(G, i)
        if oldeven and alleven:
            return False
        oldeven = alleven
    return True

def is_valid_orbit(G):
    """Is G an orbit graph?"""
    return G.is_connected() and is_full_rank(G) and twocommute(G)

# Unlike the orbit graphs for convex polytopes, the graphs for tilings can be 
# fully transitive (ie, there need not be any rank j so that the j-deleted graph
# is disconnected.)
# Also, for rank 3 specifically, the evenness condition does not apply:
# a rank 3 tiling (a tiling of the plane) can be both (0,1)-even and (1,2)-even
# (Like {4,4}). In other ranks, 3-sections are always part of a convex polytope,
# so this doesn't happen.

def is_valid_tiling_orbit(G):
    """Is G an orbit graph for a tiling?"""
# a more subtle version of intransitivity could be checked for
# (the full tiling could be fully-transitive, but each facet and vertex figure
# must not be).
# But there could be a fully-transitive facet subgraph reflecting
# a regular face which has less symmetry when embedded in the tiling.
    dim = max(G.es["rank"]) + 1
    return is_valid_orbit(G) and (dim == 3 or noadjranksnot3(G))

def is_valid_convex_orbit(G):
    """Is G an orbit graph for a convex polytope?"""
    return is_valid_orbit(G) and (G.vcount() == 1 or intransitive(G)) and noadjranksnot3(G)

def is_valid_tiling_only(G):
    """Is G a possible orbit graph for a tiling but not a convex polytope?"""
    return is_valid_tiling_orbit(G) and not is_valid_convex_orbit(G)

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
# e.g. for four:
#[[], [(0,1)], [(0,1),(2,3)], [(0,2)], [(0,2),(1,3)], [(0,3)], [(0,3),(1,2)], [(1,2)], [(1,3)], [(2,3)]]

def isomorphism_representatives(graphs, class_sizes=False):
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

def _orbit_graphs(numorbit, dim, is_valid=is_valid_orbit):
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
    ok_graphs = [g for g in all_graphs if is_valid(g)]
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
    if convex:
        return _orbit_graphs(numorbits, dim, is_valid_convex_orbit)
    return _orbit_graphs(numorbits, dim, is_valid_tiling_orbit)

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
    for X in rank_deleted_components(G, (j,l)):
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
    for X in rank_deleted_components(G, (j,l)):
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

def underlying_simple_graph(G):
    edges = {(min(e.tuple),max(e.tuple)) for e in G.es if e.source != e.target}
    return igraph.Graph(G.vcount(), edges)

def is_tree(G):
    return G.is_connected() and G.is_simple() and G.ecount() == G.vcount() - 1

def is_path(G):
    return is_tree(G) and G.maxdegree() <= 2

def partition_graphs(graphs):
    """
    Return three lists:
    - graphs whose underlying simple graph is a path,
    - graphs which are trees (but not paths),
    - and others.
    Note: the input list is modified.
    """
    paths = []
    trees = []
    for i in range(len(graphs)-1, -1, -1):
        ug = underlying_simple_graph(graphs[i])
        if is_path(ug):
            paths.append(graphs.pop(i))
        elif is_tree(ug):
            trees.append(graphs.pop(i))
    return paths, trees, graphs

def showpath(G):
    pathstr = '*'
    ug = underlying_simple_graph(G)
    path = ug.get_diameter()
    for i in range(len(path)-1):
        ranks = G.es(_between=([path[i]],[path[i+1]]))["rank"]
        ranks.sort()
        pathstr += '-' + ','.join(str(r) for r in ranks) + '-*'
    print(pathstr)

def showedges(G):
    D = max(G.es["rank"]) + 1
    for v in G.vs:
        print(f'{v.index}: ', end=' ')
        edges = set(G.incident(v))
        msgs = []
        for rank in range(D):
            e = G.es(rank=rank,_from=v)[0]
            if e.source_vertex == v:
                target = e.target
            else:
                target = e.source
            if target <= v.index:
                if target == v.index:
                    target = '↻'
                msgs.append(Style.DIM + f'{rank}: {target}' + Style.RESET_ALL)
            else:
                msgs.append(f'{rank}: {target}')
        print(', '.join(msgs))

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        sys.exit('Two arguments: dimension and number of orbits')
    dim = int(sys.argv[1])
    numorbit = int(sys.argv[2])
    for G in orbitgraphs(numorbit, dim):
        showedges(G)
        print()

