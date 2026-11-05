# Given k, what is the smallest b such that there exists a with a/b not in E_k?
import math
from fractions import Fraction
from functools import lru_cache

@lru_cache(maxsize=None)

# Check recursively if an expansion with k terms exists
def kExpansion(frac, k, min_m=1):
    if frac <= 0:
        return False
    if k == 1:
        return frac.numerator == 1 and frac.denominator >= min_m
    if frac.numerator == 1:
        return True

    m = max(-(-frac.denominator // frac.numerator), min_m)  # ceil(1/frac), integer-only
    # Largest x_1 that fits

    while True:
        # Max sum achievable with k distinct denominators starting at m
        if sum(Fraction(1, m + i) for i in range(k)) < frac: 
            return False

        # Recursive step    
        if kExpansion(frac - Fraction(1, m), k - 1, m + 1):
            return True
        m += 1


# Find the smallest b such that there exists a with a/b not in E_k
def smallestb(k):
    b = 3
    while True:
        for a in range(2,b):
            if kExpansion(Fraction(a,b), k) == False:
                print(Fraction(a,b))
                return
        b+=1

# Find the smallest k such that (b-1)/b is in E_k
def smallestk(b):
    if b < 2:
        return 
    frac = Fraction(b-1,b)
    k = 1
    while True:
        if kExpansion(frac, k):
            print(f"{frac} is minimally in E_{k}")
            return k
        k+=1



