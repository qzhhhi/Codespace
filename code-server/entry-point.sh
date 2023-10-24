#!/bin/bash

set -e

sudo chown ubuntu:ubuntu /home/ubuntu/workspace

mkdir -p /home/ubuntu/workspace/.vscode/
if ! [ -f "/home/ubuntu/workspace/.vscode/launch.json" ]; then
    cp /home/ubuntu/.vscode-server/config/launch.json /home/ubuntu/workspace/.vscode/
fi
if ! [ -f "/home/ubuntu/workspace/.vscode/tasks.json" ]; then
    cp /home/ubuntu/.vscode-server/config/tasks.json /home/ubuntu/workspace/.vscode/
fi

alias make="make CC=gcc CFLAGS='-fmax-errors=1 -g -O0 -std=c11 -Wall -Werror=implicit -Werror=shadow' CXX=g++ CXXFLAGS='-g -std=c++17'"
alias make50="make CC=gcc CFLAGS='-fmax-errors=1 -g -O0 -std=c11 -Wall -Werror=implicit -Werror=shadow' CXX=g++ CXXFLAGS='-g -std=c++17' LDLIBS=-lcs50"

code serve-web --cli-data-dir ~/.vscode-server/cli --host 0.0.0.0 --port 8080 --connection-token "${LOGIN_TOKEN}" --accept-server-license-terms