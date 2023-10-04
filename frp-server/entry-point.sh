#!/bin/bash

set -e

service nginx restart
/etc/frps/frps -c /etc/frps/frps.ini