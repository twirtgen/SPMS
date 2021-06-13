#! /bin/sh -e

CERT_NAME=root_ca

openssl genrsa -passout "pass:${PASS}" -aes256 -out ${CERT_NAME}.key 4096
openssl req -x509 -passin "pass:${PASS}" -new -nodes -key "${CERT_NAME}.key" -sha512 -days 365 -out "${CERT_NAME}.pem" -subj "/CN=SPMS_ROOT_CA"
