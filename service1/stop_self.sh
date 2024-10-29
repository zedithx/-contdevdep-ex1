#!/bin/bash

# Wait 5 seconds to allow cleanup code to finish
sleep 5
# Network name to remove
NETWORK_NAME="contdevdep-ex1_app-network"

# Retrieve the container ID of the running container
CONTAINER_ID=$1
echo "Attempting to stop and remove container with ID: $CONTAINER_ID"

docker rm -f "$CONTAINER_ID"
docker network rm "$NETWORK_NAME"
