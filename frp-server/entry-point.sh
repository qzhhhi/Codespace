#!/bin/bash

set -e

if [[ -z "${SERVER_DOMAIN}" ]]; then
    echo "Missing environment variables: SERVER_DOMAIN"
    exit 1
fi

service nginx restart

sed "s/SERVER_DOMAIN/${SERVER_DOMAIN}/g" /etc/frps/frps.toml > "/tmp/frps.toml"
/etc/frps/frps -c /tmp/frps.toml