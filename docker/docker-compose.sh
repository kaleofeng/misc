#!/bin/bash

docker-compose --project-name $1 --file docker-compose-$1.yml --env-file docker-compose-$1.env ${@:2}
