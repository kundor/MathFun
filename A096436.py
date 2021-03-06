import primesieve
from itertools import combinations_with_replacement
from math import floor, sqrt

def minsqrsum(n, maxtry=8):
    """Return a list n+1 long; array[n] is the least number of squares of primes or 1
    to sum to n, or 0 if more than maxtry are required."""
    last = floor(sqrt(n))
    facs = [0, 1] + list(primesieve.primes(last))
    numsum = [0] * (n + 1)
    for nums in combinations_with_replacement(facs, maxtry): 
        val = sum(x**2 for x in nums) 
        if val <= n: 
            notzero = sum(1 for x in nums if x) 
            if not numsum[val] or notzero < numsum[val]: 
                numsum[val] = notzero 
    return numsum

numsum = minsqrsum(10000)
out = open('b096436.txt', 'wt')
for i, n in enumerate(numsum[1:], start=1): 
     print(i, n, file=out)
out.close()     
