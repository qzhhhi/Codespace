#!/bin/bash

set -e

# The number of workers MUST be set to 1, otherwise multiple frp clients will be started.
cd /www
hypercorn --bind "127.0.0.1:5000" --workers 1 app:app &

# Generate frpc config and start frpc
/www/frpc-api-config.py
/etc/frpc/frpc --config_dir /tmp/frpc-config/api/