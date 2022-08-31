#!/bin/bash

CONTAINER_NAME="tester"
NETWORK="sistemas-distribuidos-tp0-base_testing_net"

if [ ! "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
  if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    docker start -a $CONTAINER_NAME
  else
    docker run --name $CONTAINER_NAME --network=$NETWORK tester
  fi
fi