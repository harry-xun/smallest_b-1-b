#!/usr/bin/env python3
"""
Minimal number of distinct unit fractions needed to write (b-1)/b, for a range of b.
Writes a CSV "b,k" that can be resumed if interrupted.

Usage:  python egyptian_k.py --start 2 --end 10000 --out results.csv --workers 8
"""
import argparse, os, random, sys, time
from math import gcd, isqrt
from multiprocessing import Pool

# ---------------------------------------------------------------- factoring
_SMALL = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]

def _is_prime(n):
    if n < 2: return False
    for p in _SMALL:
        if n % p == 0: return n == p
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for a in _SMALL:
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else:
            return False
    return True

def _rho(n):
    if n % 2 == 0: return 2
    while True:
        c, x = random.randrange(1, n), random.randrange(2, n)
        y, d = x, 1
        while d == 1:
            x = (x * x + c) % n
            y = (y * y + c) % n; y = (y * y + c) % n
            d = gcd(abs(x - y), n)
        if d != n: return d

_fcache = {}
def factor(n):
    """Return {prime: exponent}."""
    if n in _fcache: return _fcache[n]
    res, m = {}, n
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47):
        while m % p == 0: res[p] = res.get(p, 0) + 1; m //= p
    stack = [m] if m > 1 else []
    while stack:
        t = stack.pop()
        if t == 1: continue
        if _is_prime(t): res[t] = res.get(t, 0) + 1; continue
        d = _rho(t); stack += [d, t // d]
    if len(_fcache) > 200000: _fcache.clear()
    _fcache[n] = res
    return res

# ------------------------------------------------------- exact two-term step
LOOP_LIMIT = 3000

def _two_terms(p, q, lo):
    """p/q = 1/x + 1/y with lo <= x < y ?   Uses (px-q)(py-q) = q^2."""
    span = q // p                      # x lies in (q/p, 2q/p)
    if span <= LOOP_LIMIT:
        for x in range(max(lo, span + 1), 2 * span + 2):
            n, d = p * x - q, q * x
            if n > 0 and d % n == 0 and d // n > x:
                return True
        return False
    # large range: enumerate divisors of q^2 instead
    divs = [1]
    for pr, e in factor(q).items():
        divs = [d * pr ** i for d in divs for i in range(2 * e + 1)]
    q2 = q * q
    for d1 in divs:
        if d1 >= q or (d1 + q) % p: continue
        d2 = q2 // d1
        if (d2 + q) % p: continue
        if (d1 + q) // p >= lo:
            return True
    return False

# ------------------------------------------------------------ main search
def _exists(p, q, k, lo):
    """Is p/q a sum of exactly k distinct unit fractions with denominators >= lo?"""
    if k == 1:
        return q % p == 0 and q // p >= lo
    if k == 2:
        return _two_terms(p, q, lo)
    m = max(lo, q // p + 1)            # 1/m must be < p/q
    m_max = k * q // p                 # largest term is at least (p/q)/k
    while m <= m_max:
        n, d = p * m - q, q * m
        g = gcd(n, d)
        if _exists(n // g, d // g, k - 1, m + 1):
            return True
        m += 1
    return False

def min_k(b):
    """Smallest k such that (b-1)/b is a sum of k distinct unit fractions."""
    k = 1
    while True:
        if _exists(b - 1, b, k, 2):
            return k
        k += 1

def _work(b):
    return b, min_k(b)

# ------------------------------------------------------------------ driver
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=2)
    ap.add_argument("--end", type=int, default=10_000)
    ap.add_argument("--out", default="results.csv")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    a = ap.parse_args()

    start = a.start
    if os.path.exists(a.out):                       # resume
        last = None
        with open(a.out) as f:
            for line in f:
                if line[0].isdigit(): last = int(line.split(",")[0])
        if last is not None: start = max(start, last + 1)
    new = not os.path.exists(a.out)
    t0 = time.time()
    with open(a.out, "a") as f, Pool(a.workers) as pool:
        if new: f.write("b,k\n")
        for b, k in pool.imap(_work, range(start, a.end + 1), chunksize=4):  # ordered
            f.write(f"{b},{k}\n")
            if b % 100 == 0:
                f.flush(); print(f"b={b} k={k} ({time.time()-t0:.0f}s)", flush=True)

if __name__ == "__main__":
    main()
