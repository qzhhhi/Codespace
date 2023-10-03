#!/bin/bash

set -e

sudo rm -rf /tmp/*

LOGIN_SUBDOMAIN=$1

# FIRST_LAUNCH_DESKTOP=false
# if ! [ -f "${HOME}/fluxbox/lastwallpaper" ]; then FIRST_LAUNCH_DESKTOP=true; fi

# export DISPLAY=:7
# Xvfb ${DISPLAY} -screen 0 1920x1080x24 &
# fluxbox &
# x11vnc -forever -listen 0.0.0.0 -rfbport 5900 -noipv6 -passwd "${LOGIN_PWD}" -display :7 &

# if [ ${FIRST_LAUNCH_DESKTOP} ]; then fbsetbg /usr/share/images/fluxbox/apple.jpg; fi

# code serve-web --host 0.0.0.0 --port 8080 --connection-token S0Vcfz5p5fOWpOtR --accept-server-license-terms &
code serve-web --cli-data-dir ~/.vscode-server/cli --host 0.0.0.0 --port 8080 --without-connection-token --accept-server-license-terms &

sed "s/SUBDOMAIN/${LOGIN_SUBDOMAIN}/g" /etc/frpc/frpc.ini > "/tmp/frpc.ini"
/etc/frpc/frpc -c "/tmp/frpc.ini"