#!/usr/bin/env python3
"""
Experiment A: classical factoring timings (Pollard's Rho)
Saves CSV with measurements for each semiprime.
"""

import csv
import math
import random
import time
import secrets
import sys
from typing import Tuple, Optional, List

# ---------- Utilities: Miller-Rabin primality test ----------
def is_probable_prime(n: int, k: int = 8) -> bool:
    """Miller-Rabin probabilistic primality test."""
    if n < 2:
        return False
    small_primes = [2,3,5,7,11,13,17,19,23,29]
    for p in small_primes:
        if n % p == 0:
            return n == p
    # write n-1 as d * 2^s
    s = 0
    d = n - 1
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = secrets.randbelow(n - 3) + 2  # [2, n-2]
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        composite = True
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                composite = False
                break
        if composite:
            return False
    return True

# ---------- Prime generation ----------
def generate_prime(bits: int) -> int:
    """Generate a prime of approximately `bits` bits."""
    if bits < 2:
        raise ValueError("bits must be >= 2")
    while True:
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1  # ensure top bit and odd
        if is_probable_prime(candidate):
            return candidate

def generate_semiprime(bits: int) -> Tuple[int,int,int]:
    """Generate semiprime N = p*q with p,q ~ bits/2 bits. Returns (N,p,q)."""
    half = bits // 2
    p = generate_prime(half)
    q = generate_prime(bits - half)
    # ensure p != q
    while q == p:
        q = generate_prime(bits - half)
    return p * q, p, q

# ---------- Pollard's Rho factoring ----------
def gcd(a: int, b: int) -> int:
    return math.gcd(a, b)

def pollards_rho(n: int, max_iter: int = 1000000) -> Optional[int]:
    """Pollard's Rho for a nontrivial factor of n (probabilistic)."""
    if n % 2 == 0:
        return 2
    # random polynomial f(x) = x^2 + c mod n
    for attempt in range(10):
        x = secrets.randbelow(n - 2) + 2
        y = x
        c = secrets.randbelow(n - 1) + 1
        d = 1
        iters = 0
        while d == 1 and iters < max_iter:
            x = (x * x + c) % n
            y = (y * y + c) % n
            y = (y * y + c) % n
            d = gcd(abs(x - y), n)
            iters += 1
            if d == n:
                break
        if 1 < d < n:
            return d
    return None

def trial_division_small(n: int, limit: int = 1000) -> Optional[int]:
    """Try small primes up to `limit` to find a factor quickly."""
    # simple list of primes up to `limit`
    for p in range(2, limit + 1):
        if n % p == 0:
            return p
    return None

def factor_semiprime(n: int) -> Tuple[Optional[int], Optional[int]]:
    """Attempt to return factors p,q of semiprime n (order not guaranteed)."""
    # quick small-prime trial
    small = trial_division_small(n, limit=1000)
    if small:
        return small, n // small
    # pollard
    f = pollards_rho(n)
    if f is None:
        return None, None
    return f, n // f

# ---------- Experiment driver ----------
def run_experiment(bit_lengths: List[int], samples_per_size: int = 10, out_csv: str = "factor_results.csv"):
    random_seed = 42
    random.seed(random_seed)
    secrets_generator = random_seed  # note: secrets uses system randomness; for reproducibility, store seeds
    header = ["bit_length", "sample_index", "N", "p_true", "q_true", "factor1", "factor2", "time_s", "success"]
    with open(out_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for bits in bit_lengths:
            print(f"\n=== Bit length {bits} ({samples_per_size} samples) ===")
            for i in range(samples_per_size):
                # generate semiprime
                N, p_true, q_true = generate_semiprime(bits)
                start = time.perf_counter()
                f1, f2 = factor_semiprime(N)
                end = time.perf_counter()
                elapsed = end - start
                success = False
                if f1 is not None and f2 is not None:
                    # normalize order
                    found = sorted([int(f1), int(f2)])
                    true = sorted([int(p_true), int(q_true)])
                    success = (found == true) or (found == sorted([true[1], true[0]]))
                # write row
                writer.writerow([bits, i, N, p_true, q_true, f1, f2, round(elapsed, 6), success])
                csvfile.flush()
                print(f"bits={bits} idx={i} time={elapsed:.4f}s success={success}")
    print(f"\nResults written to {out_csv}")

# ---------- Plotting helper (optional) ----------
def quick_plot(csv_file: str):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed; install via `pip install matplotlib` to enable plotting.")
        return
    import math
    xs = []
    ys = []
    with open(csv_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["success"] == "True":
                xs.append(int(row["bit_length"]))
                ys.append(float(row["time_s"]))
    if not xs:
        print("No successful measurements to plot.")
        return
    plt.scatter(xs, ys, alpha=0.7)
    plt.yscale("log")
    plt.xlabel("bit length")
    plt.ylabel("time (seconds, log scale)")
    plt.title("Factoring time (successful runs)")
    plt.grid(True)
    plt.show()

# ---------- Main ----------
if __name__ == "__main__":
    # Example default parameters; change as needed
    # Choose bit_lengths small enough so your laptop can complete them
    BIT_LENGTHS = [16, 20, 24, 28, 32, 36]   # start small; increase as you can tolerate runtime
    SAMPLES = 8
    OUT_CSV = "factor_results.csv"

    # optional CLI overrides: python3 experiment_factor.py 24,28 10
    if len(sys.argv) >= 2:
        bits_arg = sys.argv[1]
        try:
            BIT_LENGTHS = [int(x) for x in bits_arg.split(",")]
        except Exception:
            print("Error parsing bit lengths argument. Use comma-separated ints, e.g. 16,20,24")
            sys.exit(1)
    if len(sys.argv) >= 3:
        try:
            SAMPLES = int(sys.argv[2])
        except Exception:
            pass
    print(f"Running factoring experiment with bit lengths: {BIT_LENGTHS}, samples per size: {SAMPLES}")
    run_experiment(BIT_LENGTHS, SAMPLES, OUT_CSV)
    # optional: quick_plot(OUT_CSV)
