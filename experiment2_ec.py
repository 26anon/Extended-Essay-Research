# experiment2_ec.py
# Pollard's Rho for Elliptic Curve Discrete Logarithm Problem (ECDLP)
# Experiment 2 for EE: Compare ECC hardness vs RSA factoring
# --------------------------------------------------------------

import random
import csv
import time
from math import gcd
from typing import Optional

# -----------------------------
# Elliptic curve setup
# -----------------------------
class EllipticCurve:
    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p
        if (4 * a**3 + 27 * b**2) % p == 0:
            raise ValueError("Invalid curve parameters!")

    def is_on_curve(self, P):
        if P is None:
            return True
        x, y = P
        return (y**2 - (x**3 + self.a * x + self.b)) % self.p == 0

    def add(self, P, Q):
        if P is None: return Q
        if Q is None: return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None
        if P == Q:
            m = (3 * x1**2 + self.a) * pow(2 * y1, -1, self.p)
        else:
            m = (y2 - y1) * pow(x2 - x1, -1, self.p)
        m %= self.p
        x3 = (m**2 - x1 - x2) % self.p
        y3 = (m * (x1 - x3) - y1) % self.p
        return (x3, y3)

    def mul(self, k, P):
        R = None
        while k:
            if k & 1:
                R = self.add(R, P)
            P = self.add(P, P)
            k >>= 1
        return R


# -----------------------------
# Pollard’s Rho for ECDLP
# -----------------------------
def pollards_rho_ecdlp(curve, P, Q, order, max_iter=100000):
    # Goal: Find k such that Q = kP
    def f(X, a, b):
        # Partition function into 3 subsets
        if X[0] % 3 == 0:
            return curve.add(X, P), (a + 1) % order, b
        elif X[0] % 3 == 1:
            return curve.add(X, X), (2 * a) % order, (2 * b) % order
        else:
            return curve.add(X, Q), a, (b + 1) % order

    # Initialize
    X, a, b = P, 1, 0
    X2, a2, b2 = X, a, b  # "tortoise and hare"

    for _ in range(max_iter):
        X, a, b = f(X, a, b)
        X2, a2, b2 = f(*f(X2, a2, b2))  # move twice as fast

        if X == X2:  # Collision
            r = (a - a2) % order
            s = (b2 - b) % order
            if s == 0:
                return None
            inv = pow(s, -1, order)
            return (r * inv) % order
    return None


# -----------------------------
# Experiment runner
# -----------------------------
def run_experiment():
    results = []
    primes = [97, 193, 257, 521]  # small primes for curves
    for p in primes:
        curve = EllipticCurve(a=2, b=3, p=p)
        G = (3, 6)
        assert curve.is_on_curve(G)

        order = p  # not exact, but works for toy curves
        k = random.randint(2, order - 1)
        Q = curve.mul(k, G)

        start = time.time()
        found_k = pollards_rho_ecdlp(curve, G, Q, order)
        elapsed = time.time() - start

        results.append({
            "prime": p,
            "order": order,
            "true_k": k,
            "found_k": found_k,
            "success": found_k == k,
            "time_s": elapsed
        })

    # Save results
    with open("ecc_pollard_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)


if __name__ == "__main__":
    run_experiment()
    print("✅ ECC Pollard’s Rho experiment complete! Results saved to ecc_pollard_results.csv")
