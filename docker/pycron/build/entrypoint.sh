#!/bin/bash
set -eo pipefail
shopt -s nullglob

crontab /data/script/crontabs

exec "$@"
