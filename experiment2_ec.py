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

    def point_add(self, P, Q):
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
                R = self.point_add(R, P)
            P = self.point_add(P, P)
            k >>= 1
        return R


# ----------------------------
# Discrete log (brute force)
# ----------------------------

def discrete_log_bruteforce(curve, P, Q, max_iter=1_000_000):
    """Try to recover k from Q = kP"""
    R = None
    for k in range(1, max_iter):
        R = curve.point_add(R, P)
        if R == Q:
            return k, k
    return None, max_iter


# ----------------------------
# Experiment runner
# ----------------------------

def run_experiment(bit_lengths=[16, 20, 24, 28, 32], samples=5, filename="ecc_results.csv"):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["bit_length", "sample_index", "p", "a", "b", "P", "Q", "k_true", "k_found", "time_s", "success"])

        for bits in bit_lengths:
            # Pick a random prime ~ size 2^bits
            while True:
                p = random.getrandbits(bits)
                if isprime(p):
                    break
            a = random.randint(0, p-1)
            b = random.randint(0, p-1)
            curve = EllipticCurve(a, b, p)

            # Pick a random point on the curve
            # Brute-force find a valid point
            P = None
            for x in range(1, p):
                y2 = (x*x*x + a*x + b) % p
                for y in range(p):
                    if (y*y) % p == y2:
                        P = (x, y)
                        break
                if P: break

            if not P:
                continue  # skip if no point found (rare)

            for i in range(samples):
                k_true = random.randint(2, p-1)
                Q = curve.scalar_mult(k_true, P)

                start = time.time()
                k_found, iters = discrete_log_bruteforce(curve, P, Q, max_iter=100000)
                elapsed = time.time() - start

                success = (k_found == k_true)
                writer.writerow([bits, i, p, a, b, P, Q, k_true, k_found, elapsed, success])
                print(f"[{bits} bits] Sample {i} -> Success: {success}, Time: {elapsed:.6f}s")


if __name__ == "__main__":
    run_experiment()
