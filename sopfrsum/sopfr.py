#from numba import jit
#import numpy as np
from primefac import primefac
#import sympy
#from sympy import factorint
#from sympy.abc import i,m #,n
#from sympy.utilities.lambdify import lambdify

# Timing, for k in range(1, 10), n in range(2,20000)
# numpy sumpow (incorrect) + primefac:    1m37s
# numpy cumsumpow (incorrect) + primefac: 1m27s
# lambdify + primefac:                   29m18s
# summat + primefac:                      8m33s real (24m03s user)
# pypy summat + primefac:              > 11m41s (died from too many open files)
# summat as_poly + primefac:              6m50s real (22m user)
# pypy poly + primefac:                 > 3m03s (died from too many open files)

# python sumpow + primefac:              28m41s
# pypy sumpow + primefac:                32m45s real (user 83m45s)

# keep sum + primefac:                    6m40s (user 22m39s)
# pypy keep sum + primefac:              22m41s
# jit keep sum + primefac:                6m35s

# numpy sumpow (incorrect) + factorint:  11m54s
# lambdify + factorint:                  80m27s
# summat + factorint:                  > 54m20s
# poly + factorint:                      74m07s

# bash, bc, factor, awk:                  0m54s
#   But for some tests, like 11th power, seems to be much slower!

# msieve code:                            1m12s
# pari/gp:                                3m58s

# Trial division by small primes (only less than n; otherwise, we can give up): 15s python
# ditto, with c and gmp:                    02s

#@njit 
#def sumpow(n, m): 
#    # breaks for 77936,3 or 8566,4
#    return np.sum(np.arange(n+1)**m)

#sumpow = lambdify((n,m), sympy.summation(i**m, (i, 1, n)), 'numpy')

#def sumpow(n, m):
#    return sum(i**m for i in range(n+1))

#def primefac(n):
#    try:
#        return factorint(n, multiple=True)
#    except MemoryError:
#        sympy.numbers._gcdcache.clear()
#        return factorint(n, multiple=True)

#summat = sympy.summation

# @jit
# def checkit(k, maxn):
#     sumpow = 1
#     for n in range(2,maxn):
#         sumpow += n**k
#         if sum(primefac(sumpow)) == n:
#             print('g(f(', n, ',', k, ')) = ',n)

for k in range(1,90):
#    poly = summat(i**k, (i, 1, m)).as_poly()
    print(k)
    sumpow = 1
    for n in range(2,90000):
        sumpow += n**k
        if sum(primefac(sumpow)) == n:
#        if sum(primefac(int(summat(i**k, (i, 1, n))))) == n:
#        if sum(primefac(sumpow(n, k))) == n:
#        if sum(primefac(int(poly(n)))) == n:
#        if sum(factorint(sumpow(n, k), multiple=True)) == n:
#        if sum(factorint(summat(i**k, (i, 1, n)), multiple=True)) == n:
#        if sum(factorint(poly(n), multiple=True)) == n:
            print(f'g(f({n},{k})) = {n}')
