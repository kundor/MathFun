# Unlike the orbit graphs for convex polytopes, the graphs for tilings can be 
# fully transitive (ie, there need not be any rank j so that the j-deleted graph
# is disconnected.)
# Also, for rank 3 specifically, the evenness condition does not apply:
# a rank 3 tiling (a tiling of the plane) can be both (0,1)-even and (1,2)-even
# (Like {4,4}). In other ranks, 3-sections are always part of a convex polytope,
# so this doesn't happen.

from orbitgraph import *
from itertools import combinations, product

def showedges(G):
    print('\n'.join(str((e.tuple, e['rank'])) for e in G.es))

def alledgesets(verts):
    curedges = [[]]
    for pair in combinations(verts, 2):
        remverts = verts - set(pair)
        for edges in alledgesets(remverts):
            curedges.append([pair] + edges)
    return curedges


def possedgesets(numorbit):
    allsets = alledgesets(set(range(numorbit)))
    poss_rank_edges = []
    for es in allsets:
        if sorted(es) in poss_rank_edges:
            continue
        poss_rank_edges.append(es)
    return poss_rank_edges

numorbit = 4
dim = 3

possible_irank_edgesets = possedgesets(numorbit)
# e.g. for four:
#[[], [(0,1)], [(0,1),(2,3)], [(0,2)], [(0,2),(1,3)], [(0,3)], [(0,3),(1,2)], [(1,2)], [(1,3)], [(2,3)]]

all_graphs = []

for rankedges in product(possible_irank_edgesets, repeat=dim):
    edgeranks = []
    for rank, edges in enumerate(rankedges):
        edgeranks += [rank] * len(edges)
    graph_edges = sum(rankedges, [])
    G = igraph.Graph(numorbit, graph_edges, edge_attrs={'rank': edgeranks})
    addloops(G, dim)
    all_graphs.append(G)

con_graphs = [g for g in all_graphs if g.is_connected()]
discon_graphs = [g for g in all_graphs if not g.is_connected()]

ztc_graphs = [g for g in con_graphs if twocommute(g)]
nonztc_graphs = [g for g in con_graphs if not twocommute(g)]

isom_class_reps = []
isom_class_nums = []
for g in ztc_graphs:
    for i,k in enumerate(isom_class_reps):
        if isomorphicorbits(g, k):
            isom_class_nums[i] += 1
            break
    else:
        isom_class_reps.append(g)
        isom_class_nums.append(1)

assert sum(isom_class_nums) == len(ztc_graphs)

for G in isom_class_reps:
    showedges(G)
    print()
