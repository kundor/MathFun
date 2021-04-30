# Concrete Mathematics problem 1.21:
# Suppose there are 2n people in a circle; the first n are "good guys"
# and the last n are "bad guys".
# In the problem we show there is always a q such that executing every q-th person
# get all the bad guys first. Namely, the least common multiple of n+1, n+2, ..., 2n
# will work.
# However, a smaller q can (always?) be found.
# e.g. for n = 3, q = 5 suffices, less than lcm(4,5,6) = 60.

# submitted to OEIS as A343780

import itertools

def firstn(n, q):
    """Do the first n survive when eliminating every q-th person out of 2n?"""
    circle = list(range(2*n))
    i = 1
    while len(circle) > n:
        i = (i + q - 1) % len(circle)
        if circle[i] > 0 and circle[i] <= n:
            return False
        circle.pop(i)
    return True

vals = []

for n in range(1,22):
    for q in itertools.count(n+1):
        if firstn(n, q):
            print(f'{n:2}: {q}')
            vals.append(q)
            break

# Graham, Knuth and Patashnik say "A non-rigorous argument suggests that a `random'
# value of q will succeed with probability 1 / (2n C n) ~ sqrt(πn)/4^n,
# so we might expect to find such a q less than 4^n."

# Compare to 4^n and lcm bounds
from collections import Counter
import operator
from functools import reduce

try:
    from primefac import factorint
except (ImportError, SyntaxError):
    from sympy import factorint

def lcm(nums):
    factors = Counter()
    for n in nums:
        factors |= factorint(n)
    return reduce(operator.mul, factors.elements(), 1)

width = 21

for n,v in enumerate(vals,1):
    cf1 = 4**n
    cf2 = lcm(range(n+1,2*n+1))
    cmp1 = '<' if v < cf1 else '>'
    cmp2 = '<' if cf1 < cf2 else '>'
    print(f'{v:{width},} {cmp1} {cf1:{width},} {cmp2} {cf2:{width},}')

