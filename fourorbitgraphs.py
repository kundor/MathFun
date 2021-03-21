# Unlike the orbit graphs for convex polytopes, the graphs for tilings can be 
# fully transitive (ie, there need not be any rank j so that the j-deleted graph
# is disconnected.)
# Also, for rank 3 specifically, the evenness condition does not apply:
# a rank 3 tiling (a tiling of the plane) can be both (0,1)-even and (1,2)-even
# (Like {4,4}). In other ranks, 3-sections are always part of a convex polytope,
# so this doesn't happen.

from orbitgraph import *

def showedges(G):
    print('\n'.join(str((e.tuple, e['rank'])) for e in G.es))

possible_irank_edgesets = [[],
        [(0,1)],
        [(0,1),(2,3)],
        [(0,2)],
        [(0,2),(1,3)],
        [(0,3)],
        [(0,3),(1,2)],
        [(1,2)],
        [(1,3)],
        [(2,3)]]
all_graphs = []
for zedges in possible_irank_edgesets:
    for oedges in possible_irank_edgesets:
        for tedges in possible_irank_edgesets:
            edgeranks = [0]*len(zedges) + [1]*len(oedges) + [2]*len(tedges)
            G = igraph.Graph(4, zedges + oedges + tedges, edge_attrs={'rank': edgeranks})
            addloops(G,3)
            all_graphs.append(G)

con_graphs = [g for g in all_graphs if g.is_connected()]
discon_graphs = [g for g in all_graphs if not g.is_connected()]

ztc_graphs = [g for g in con_graphs if twocommute(g)]
nonztc_graphs = [g for g in con_graphs if not twocommute(g)]

[(e.tuple, e['rank']) for e in G.es]

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
