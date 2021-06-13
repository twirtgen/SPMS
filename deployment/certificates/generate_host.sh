#! /bin/sh -e

KEY="${NAME}.key"
CSR="${NAME}.csr"
CRT="${NAME}.pem"

ROOT_CA_KEY="${ROOT_CA}.key"
ROOT_CA_PEM="${ROOT_CA}.pem"

# Generate private key for PV
openssl genrsa -passout "pass:${PASS}" -aes256 -out "${KEY}" 4096

# Generate CSR for PV
openssl req -batch -passin "pass:${PASS}" -new -key "${KEY}" -out "${CSR}"

CONFIG="$(mktemp)"
cat <<EOF > "${CONFIG}"
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = ${NAME}
IP.1 = ${IP}
EOF

# Sign CSR with root CA certificate
openssl x509 -passin "pass:${ROOT_CA_PASS}" -req -in "${CSR}" -CA "${ROOT_CA_PEM}" -CAkey "${ROOT_CA_KEY}" -CAcreateserial -out "${CRT}" -days 365 -sha256 -extfile "${CONFIG}"

rm "${CONFIG}"

openssl verify -CAfile "${ROOT_CA_PEM}" "${CRT}"
