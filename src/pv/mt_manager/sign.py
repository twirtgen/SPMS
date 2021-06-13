from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography import x509

KEY_PATH = '/dev/shm/pv.key'
CRT_PATH = '/dev/shm/pv.crt'

private_key = None
crt = None

with open(KEY_PATH, "rb") as key_file:
    private_key = serialization.load_pem_private_key(key_file.read(), password=None)

with open(CRT_PATH, "rb") as crt_file:
    crt = x509.load_pem_x509_certificate(crt_file.read())

def get_crt() -> str:
    return crt.public_bytes(serialization.Encoding.PEM).hex()

def sign(message):
    return private_key.sign(message, padding.PSS(mgf=padding.MGF1(crt.signature_hash_algorithm), salt_length=padding.PSS.MAX_LENGTH), crt.signature_hash_algorithm)
