import time
from statistics import mean
from cryptography.hazmat.primitives.asymmetric import rsa, ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

NUM_RUNS = 20

def benchmark_rsa(key_size=2048):
    times = {"keygen": [], "sign": [], "verify": [], "encrypt": [], "decrypt": []}
    for _ in range(NUM_RUNS):
        # Key generation
        t0 = time.time()
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
        t1 = time.time()
        times["keygen"].append(t1 - t0)

        public_key = private_key.public_key()

        # Sign
        message = b"Test message for RSA"
        t0 = time.time()
        signature = private_key.sign(
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        t1 = time.time()
        times["sign"].append(t1 - t0)

        # Verify
        t0 = time.time()
        public_key.verify(
            signature,
            message,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        t1 = time.time()
        times["verify"].append(t1 - t0)

        # Encrypt
        t0 = time.time()
        ciphertext = public_key.encrypt(
            message,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        t1 = time.time()
        times["encrypt"].append(t1 - t0)

        # Decrypt
        t0 = time.time()
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        t1 = time.time()
        times["decrypt"].append(t1 - t0)

    return {k: mean(v) for k, v in times.items()}


def benchmark_ecc(curve=ec.SECP256R1()):
    times = {"keygen": [], "sign": [], "verify": []}
    for _ in range(NUM_RUNS):
        # Key generation
        t0 = time.time()
        private_key = ec.generate_private_key(curve)
        t1 = time.time()
        times["keygen"].append(t1 - t0)

        public_key = private_key.public_key()

        # Sign
        message = b"Test message for ECC"
        t0 = time.time()
        signature = private_key.sign(message, ec.ECDSA(hashes.SHA256()))
        t1 = time.time()
        times["sign"].append(t1 - t0)

        # Verify
        t0 = time.time()
        public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        t1 = time.time()
        times["verify"].append(t1 - t0)

    return {k: mean(v) for k, v in times.items()}


if __name__ == "__main__":
    print("RSA-2048:", benchmark_rsa(2048))
    print("RSA-3072:", benchmark_rsa(3072))
    print("ECC-P256:", benchmark_ecc(ec.SECP256R1()))
    print("ECC-P384:", benchmark_ecc(ec.SECP384R1()))
