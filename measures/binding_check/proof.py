from hashlib import sha256
from time import perf_counter
from statistics import variance, mean

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography import x509
import requests


def proof(auth_path: dict, binding: bytes) -> bytes:
    binding_hash = sha256(binding).digest()
    initial_hash = sha256(bytes.fromhex(''.join([binding_hash.hex()]+auth_path['leaves']))).digest() if 'leaves' in auth_path else binding_hash
    cumulator = initial_hash

    for node in sorted(auth_path, key=len, reverse=True):
            if node == 'leaves':
                    continue
            other_hash = bytes.fromhex(auth_path[node])
            s = cumulator + other_hash if node[-1] == '1' else other_hash + cumulator
            cumulator = sha256(s).digest()

    return cumulator

def operate():
    begin1 = perf_counter()
    r = requests.get('http://10.20.3.100/binding/be.michelfra.disable_cc00')
    binding = r.content

    r = requests.get('http://10.20.3.100/lookup/usr/be.michelfra.disable_cc00')
    path = r.json()

    r = requests.get('http://10.20.3.100/str')
    pv_str = bytes.fromhex(r.json())

    begin2 = perf_counter()
    root_hash = proof(path, binding)
    begin3 = perf_counter()

    public_key.verify(pv_str, root_hash, padding.PSS(mgf=padding.MGF1(pem.signature_hash_algorithm), salt_length=padding.PSS.MAX_LENGTH), pem.signature_hash_algorithm)

    end = perf_counter()

    return {'req_duration': begin2 - begin1, 'proof_duration': begin3 - begin2, 'sigval_duration': end - begin3, 'proof_sigval_duration': end - begin2}

    """
    print('Successful check')
    print('Requests %f' % (begin2 - begin1))
    print('Proof %f' % (begin3 - begin2))
    print('Signature validation %f' % (end - begin3))
    print('Total %f' % (end - begin1))
    """


if __name__ == '__main__':

    with open('pv.crt', 'rb') as fp:
        pem = x509.load_pem_x509_certificate(fp.read())
    public_key = pem.public_key()

    data = {'req_duration': [], 'proof_duration': [], 'sigval_duration': [], 'proof_sigval_duration': []}
    for i in range(0, 20):
        for key, value in operate().items():
            data[key].append(value)

    print(data)
    for key, value in data.items():
        print('%s : mean <%f> : variance <%f>' % (key, mean(value), variance(value)))
  


