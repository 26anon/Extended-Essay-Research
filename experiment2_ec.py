import random
import time
import csv
from sympy.ntheory import isprime

# ----------------------------
# Toy elliptic curve functions
# ----------------------------

class EllipticCurve:
    def __init__(self, a, b, p):
        self.a = a
        self.b = b
        self.p = p  # prime modulus

    def is_on_curve(self, P):
        if P is None:
            return True
        x, y = P
        return (y * y - (x * x * x + self.a * x + self.b)) % self.p == 0

    def add(self, P, Q):
        if P is None: return Q
        if Q is None: return P

        x1, y1 = P
        x2, y2 = Q

        if x1 == x2 and (y1 + y2) % self.p == 0:
            return None

        if P == Q:
            m = (3 * x1 * x1 + self.a) * pow(2 * y1, -1, self.p)
        else:
            m = (y2 - y1) * pow(x2 - x1, -1, self.p)

        m %= self.p
        x3 = (m * m - x1 - x2) % self.p
        y3 = (m * (x1 - x3) - y1) % self.p
        return (x3, y3)

    def scalar_mult(self, k, P):
        R = None
        while k:
            if k & 1:
                R = self.add(R, P)
            P = self.add(P, P)
            k >>= 1
        return R


# ----------------------------
# Pollard’s Rho for ECDLP
# ----------------------------

def pollards_rho_ecdlp(curve, P, Q, order, max_iter=100000):
    """
    Solve Q = kP using Pollard's Rho.
    Returns k or None if not found within max_iter.
    """

    def f(X, a, b):
        if X is None:  # handle point at infinity
            return P, (a + 1) % order, b

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
        X2, a2, b2 = f(*f(X2, a2, b2))  # hare moves twice as fast

        if X == X2:  # Collision
            r = (a - a2) % order
            s = (b2 - b) % order
            if s == 0:
                return None
            inv = pow(s, -1, order)
            return (r * inv) % order

    return None


# ----------------------------
# Experiment runner
# ----------------------------

def run_experiment(bit_lengths=[16, 20, 24, 28, 32], samples=5, filename="ecc_results.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["bit_length", "sample_index", "p", "a", "b", "P", "Q",
                         "k_true", "k_found", "time_s", "success"])

        for bits in bit_lengths:
            # Pick a random prime ~ size 2^bits
            while True:
                p = random.getrandbits(bits)
                if isprime(p):
                    break
            a = random.randint(0, p - 1)
            b = random.randint(0, p - 1)
            curve = EllipticCurve(a, b, p)

            # Find a random valid point P on the curve
            P = None
            for x in range(1, p):
                y2 = (x * x * x + a * x + b) % p
                for y in range(p):
                    if (y * y) % p == y2:
                        P = (x, y)
                        break
                if P: break
            if not P:
                continue  # skip if no point found

            order = p  # crude assumption, okay for toy experiments

            for i in range(samples):
                k_true = random.randint(2, p - 1)
                Q = curve.scalar_mult(k_true, P)

                start = time.time()
                k_found = pollards_rho_ecdlp(curve, P, Q, order)
                elapsed = time.time() - start

                success = (k_found == k_true)
                writer.writerow([bits, i, p, a, b, P, Q,
                                 k_true, k_found, elapsed, success])


if __name__ == "__main__":
    run_experiment()
