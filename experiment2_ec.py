# experiment2_csv.py
"""
Brute-force ECC discrete-log experiment.
Writes results to ecc_results.csv and (optionally) ecc_runtime.png.
WARNING: brute-force discrete-log is exponential; restrict max_k to keep this runnable.
"""

import time
import csv
import random
import statistics
from tinyec import registry

# Optional plotting (install matplotlib if you want plots)
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB = True
except Exception:
    MATPLOTLIB = False


def brute_force_dlog(G, Q, max_k):
    """
    Naive brute-force discrete log: find k such that k*G == Q.
    Returns found_k or None if not found within max_k steps.
    """
    if Q == G:
        return 1
    current = G
    k = 1
    while k <= max_k:
        if current == Q:
            return k
        current = current + G
        k += 1
    return None


def curve_bit_length(curve):
    """Best-effort extraction of bit-length for the curve."""
    try:
        return curve.field.p.bit_length()
    except Exception:
        try:
            return curve.curve.p.bit_length()
        except Exception:
            # fallback mapping for common tinyec names
            mapping = {"secp128r1": 128, "secp160r1": 160, "secp192r1": 192, "secp224r1": 224}
            return mapping.get(curve.name, None)


def run_experiment(curve_names, samples_per_curve=5, max_secret=5000, max_k=1000, out_csv="ecc_results.csv"):
    """
    curve_names: list of tinyec curve names (e.g., ["secp128r1", "secp160r1"])
    samples_per_curve: how many random secrets to test per curve
    max_secret: upper bound for generated secret (keep small so brute force completes)
    max_k: maximum steps brute force will attempt (safety)
    """
    rows = []
    sample_index = 0

    for curve_name in curve_names:
        curve = registry.get_curve(curve_name)
        G = curve.g
        bits = curve_bit_length(curve)
        for i in range(samples_per_curve):
            sample_index += 1
            secret_k = random.randint(1, max_secret)
            Q = secret_k * G

            t0 = time.perf_counter()
            found_k = brute_force_dlog(G, Q, max_k=max_k)
            t1 = time.perf_counter()

            time_s = t1 - t0
            success = (found_k == secret_k)
            # If found_k is not None we record it, else record ''
            rows.append([curve_name, bits, i+1, secret_k, found_k if found_k is not None else "", round(time_s, 6), success])

            print(f"[{curve_name}] sample {i+1}: secret={secret_k} found={found_k} time={time_s:.6f}s success={success}")

    # Write CSV
    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["curve_name", "bit_length", "sample_index", "secret_k", "found_k", "time_s", "success"])
        writer.writerows(rows)

    print(f"\nSaved results to {out_csv}")

    # Optional plot
    if MATPLOTLIB:
        # aggregate median time by bit_length
        agg = {}
        for r in rows:
            _bits = r[1]
            _time = r[5]
            if _bits not in agg:
                agg[_bits] = []
            agg[_bits].append(_time)

        x = sorted(agg.keys())
        y = [statistics.median(agg[b]) for b in x]

        plt.figure(figsize=(6,4))
        plt.scatter(x, y)
        plt.plot(x, y, linestyle="--", alpha=0.6)
        plt.yscale("log")          # plot time on log scale (helpful for exponential scaling)
        plt.xlabel("Curve bit length")
        plt.ylabel("Median brute-force time (s, log scale)")
        plt.title("ECC brute-force runtime (naive DLOG)")
        plt.grid(True, which="both", ls=":", alpha=0.5)
        plt.tight_layout()
        plt.savefig("ecc_runtime.png")
        print("Saved plot to ecc_runtime.png")
    else:
        print("matplotlib not available: skipping plot (pip install matplotlib to enable)")

if __name__ == "__main__":
    # Choose small curves and small max_secret for demonstration.
    curves = ["secp128r1", "secp160r1", "secp192r1"]   # example choices
    run_experiment(curves, samples_per_curve=5, max_secret=2000, max_k=2000, out_csv="ecc_results.csv")
