# Quantum resource estimates for RSA vs ECC (Shor's algorithm)
# Based on Gidney & Ekerå (2019) and NIST PQC reports

def rsa_qubits(key_size):
    """
    Estimate logical qubits needed for RSA factoring
    Reference: ~20n qubits for RSA-n factoring with optimizations
    """
    return 20 * key_size

def ecc_qubits(curve_bits):
    """
    Estimate logical qubits needed for ECC discrete log
    Reference: ~6n qubits for ECDLP with optimizations
    """
    return 6 * curve_bits

def runtime_estimate(qubits, gates_per_qubit=1e9):
    """
    Rough runtime estimate (in days) assuming 1e9 gates/sec.
    This is very optimistic (real quantum computers are slower).
    """
    total_gates = qubits * gates_per_qubit
    seconds = total_gates / 1e9
    return seconds / (60 * 60 * 24)

def main():
    # RSA estimates
    rsa_2048_qubits = rsa_qubits(2048)
    rsa_3072_qubits = rsa_qubits(3072)

    # ECC estimates
    ecc_p256_qubits = ecc_qubits(256)
    ecc_p384_qubits = ecc_qubits(384)

    print("=== Quantum Resource Estimates ===")
    print(f"RSA-2048: {rsa_2048_qubits:,} qubits, ~{runtime_estimate(rsa_2048_qubits):.2f} days")
    print(f"RSA-3072: {rsa_3072_qubits:,} qubits, ~{runtime_estimate(rsa_3072_qubits):.2f} days")
    print(f"ECC-P256: {ecc_p256_qubits:,} qubits, ~{runtime_estimate(ecc_p256_qubits):.2f} days")
    print(f"ECC-P384: {ecc_p384_qubits:,} qubits, ~{runtime_estimate(ecc_p384_qubits):.2f} days")

if __name__ == "__main__":
    main()
