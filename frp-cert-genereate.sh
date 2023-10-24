#!/bin/bash

set -e

cat > frp-openssl.cnf << EOF
[ ca ]
default_ca = CA_default
[ CA_default ]
x509_extensions = usr_cert
[ req ]
default_bits        = 2048
default_md          = sha256
default_keyfile     = privkey.pem
distinguished_name  = req_distinguished_name
attributes          = req_attributes
x509_extensions     = v3_ca
string_mask         = utf8only
[ req_distinguished_name ]
[ req_attributes ]
[ usr_cert ]
basicConstraints       = CA:FALSE
nsComment              = "OpenSSL Generated Certificate"
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid,issuer
[ v3_ca ]
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints       = CA:true
EOF

# build ca certificates
if ! [ -f "./frp-ca.key" ]; then
    openssl genrsa -out frp-ca.key 2048
fi
openssl req -x509 -new -nodes -key frp-ca.key -subj "/CN=alliance.ca.com" -days 5000 -out frp-ca.crt

# build frps certificates
openssl genrsa -out frp-server.key 2048
openssl req -new -sha256 -key frp-server.key \
    -subj "/C=XX/ST=DEFAULT/L=DEFAULT/O=DEFAULT/CN=server.com" \
    -reqexts SAN \
    -config <(cat frp-openssl.cnf <(printf "\n[SAN]")) \
    -out frp-server.csr
openssl x509 -req -days 365 -sha256 \
	-in frp-server.csr -CA frp-ca.crt -CAkey frp-ca.key -CAcreateserial \
	-extfile <(printf "subjectAltName=DNS:localhost,IP:127.0.0.1,DNS:your.frps.domain") \
	-out frp-server.crt

# build frpc certificates
openssl genrsa -out frp-client.key 2048
openssl req -new -sha256 -key frp-client.key \
    -subj "/C=XX/ST=DEFAULT/L=DEFAULT/O=DEFAULT/CN=client.com" \
    -reqexts SAN \
    -config <(cat frp-openssl.cnf <(printf "\n[SAN]")) \
    -out frp-client.csr
openssl x509 -req -days 365 -sha256 \
    -in frp-client.csr -CA frp-ca.crt -CAkey frp-ca.key -CAcreateserial \
	-out frp-client.crt

rm ./frp-server.csr ./frp-client.csr ./frp-openssl.cnf

mkdir -p ./frp-server/cert ./control-server/cert/

mv ./frp-server.key ./frp-server.crt ./frp-server/cert/
mv ./frp-client.key ./frp-client.crt ./control-server/cert/

cp ./frp-ca.crt ./frp-server/cert/
cp ./frp-ca.crt ./control-server/cert/
rm ./frp-ca.crt
