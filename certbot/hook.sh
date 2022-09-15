#!/bin/bash

CURRENT_DIR=$(cd $(dirname $0); pwd)

opertion=$1
provider_name=$2
secret_id=$3
secret_key=$4
domain=$5

hall_file=${CURRENT_DIR}/hall.py
python ${hall_file} ${opertion} ${provider_name} ${secret_id} ${secret_key} ${domain} ${CERTBOT_DOMAIN} ${CERTBOT_VALIDATION}

if [[ "${opertion}" == "add" ]]; then
    sleep 15s
fi
