import sympy
from sympy.abc import i,n,m
from sympy.utilities.lambdify import lambdify

primefac = sympy.factorint

sumpow = lambdify((n,m), sympy.summation(i**m, (i, 1, n)), 'numpy')

for k in range(1,10):
    for n in range(2,20000):
        if sum(primefac(sumpow(n,k), multiple=True)) == n:
            print(f'g(f({n},{k})) = {n}')
