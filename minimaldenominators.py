import argparse
import csv
from fractions import Fraction
from functools import lru_cache


@lru_cache(maxsize=None)
def kExpansion(frac, k, min_m=1):
    """Check whether frac has an expansion with at most k distinct terms."""
    if frac <= 0:
        return False

    if k == 1:
        return frac.numerator == 1 and frac.denominator >= min_m

    if frac.numerator == 1 and frac.denominator >= min_m:
        return True

    m = max(-(-frac.denominator // frac.numerator), min_m)

    while True:
        if sum(Fraction(1, m + i) for i in range(k)) < frac:
            return False

        if kExpansion(frac - Fraction(1, m), k - 1, m + 1):
            return True

        m += 1


def smallestb(k):
    b = 3
    while True:
        print(f"Checking b={b}", flush=True)
        for a in range(2, b):
            if not kExpansion(Fraction(a, b), k):
                print(Fraction(a, b), flush=True)
                return
        b += 1


def smallestk(b):
    if b < 2:
        return

    frac = Fraction(b - 1, b)
    k = 1
    while True:
        if kExpansion(frac, k):
            print(f"{frac} is minimally in E_{k}", flush=True)
            return k
        k += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("max_b", type=int)
    args = parser.parse_args()

    with open("results.csv", "w", newline="") as results:
        writer = csv.writer(results)
        writer.writerow(["b", "k"])

        for b in range(2, args.max_b + 1):
            print(f"Checking b={b}", flush=True)
            k = smallestk(b)
            writer.writerow([b, k])
            results.flush()
            kExpansion.cache_clear()

