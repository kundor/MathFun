#from numba import njit
import numpy as np
from primefac import primefac

# by doing cumsum up front, we take only 1m27s (instead of 1m36s)
# for k = 1 to 10, n = 1 to 20000

# agh it totally breaks when it overflows a 64-bit int tho
# like already for 3rd powers up to 77936 for example
# or 4th powers up to 8566

#@njit 
#def sumpow(n, m): 
#    return np.sum(np.arange(n+1)**m)

for k in range(1,10):
    for n,snp in enumerate(np.cumsum(np.arange(1,20000)**k).tolist(), 1):
        if sum(primefac(snp)) == n:
            print(f'g(f({n},{k})) = {n}')
