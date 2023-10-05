#!/bin/bash

set -e

sudo chown ubuntu:ubuntu /home/ubuntu/workspace

if [[ -z "${WEBSITE_SUBDOMAIN}" ]]; then
    echo "Missing environment variables: WEBSITE_SUBDOMAIN"
    exit 1
fi
if [[ -z "${LOGIN_TOKEN}" ]]; then
    echo "Missing environment variables: LOGIN_TOKEN"
    exit 1
fi

code serve-web --cli-data-dir ~/.vscode-server/cli --host 0.0.0.0 --port 8080 --connection-token "${LOGIN_TOKEN}" --accept-server-license-terms &

sed "s/SUBDOMAIN/${WEBSITE_SUBDOMAIN}/g" /etc/frpc/frpc.ini > "/tmp/frpc.ini"
sed "s/SERVER_DOMAIN/rm-alliance.work/g" /tmp/frpc.ini > "/tmp/frpc1.ini"
sed "s/SERVER_DOMAIN/rm-alliance.tech/g" /tmp/frpc.ini > "/tmp/frpc2.ini"

/etc/frpc/frpc -c "/tmp/frpc1.ini" &
/etc/frpc/frpc -c "/tmp/frpc2.ini"