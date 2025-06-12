#!/bin/bash

bash build-docker-images.sh

# Sudo is typically not required on Mac OS
if [[ $(uname) == "Darwin" ]]; then
    docker-compose up
    docker-compose down
else
    sudo docker-compose up
    sudo docker-compose down
fi
