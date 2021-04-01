"""
Generating valid vertex-types for uniform tilings of the hyperbolic plane
as given by the conditions in "Semi-regular tilings of the hyperbolic plane"
by B. Datta and S. Gupta, arXiv:1806.11393 or http://dx.doi.org/10.1007/s00454-019-00156-0
Discrete & Computational Geometry 65, 531--553.
"""
import itertools

def is_sublist(seq1, seq2):
    """Does seq1 occur in cyclic order in seq2?"""
    n, m = len(seq1), len(seq2)
    for i in range(m):
        for j in range(n):
            if seq1[j] != seq2[(i+j) % m]:
                break
        else:
            return True
    return False

def angle_sum(seq):
    return sum((k-2)/k for k in seq)

def dg_cond_a(seq):
    n = len(seq)
    for i in range(n):
        if not is_sublist((seq[(i + 1) % n], seq[i]), seq):
            return False
    return True

def dg_cond_b(seq):
    n = len(seq)
    twoples = {(seq[i], seq[(i+1) % n]) for i in range(n)}
    for x,y in twoples:
        for w,z in twoples:
            if y == w:
                if not is_sublist((x,y,z), seq):
                    return False
    return True

def dg_ok(seq):
    return angle_sum(seq) > 2 and dg_cond_a(seq) and dg_cond_b(seq)

# e.g. all valid types of degree 4 with polygon sizes up to 7 
[z for z in itertools.product(range(4,8), repeat=4) if dg_ok(z)]

def ok_seqs(n):
    """All ok sequences of length n, removing cyclic repetitions"""
    top = max(5, 4 + n//2)
    seqs = [z for z in itertools.product(range(4,top), repeat=n) if dg_ok(z)]
    uniqs = []
    for s in seqs:
        for u in uniqs:
            if is_sublist(s, u):
                break
        else:
            uniqs.append(s)
    return uniqs

def vtype(seq):
    """vertex type coded with letters for differing k_i"""
    elts = sorted(set(seq))
    reps = {e : chr(i) for i,e in enumerate(elts, start=ord('a'))}
    return [reps[n] for n in seq]

def ok_vtypes(n):
    return {''.join(vtype(s)) for s in ok_seqs(n)}


