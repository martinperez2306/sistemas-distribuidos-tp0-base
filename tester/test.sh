#!/bin/bash

CONTAINER_NAME="tester"
NETWORK="sistemas-distribuidos-tp0-base_testing_net"

if [ ! "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
  if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    docker start $CONTAINER_NAME
  else
    docker run -dt --name $CONTAINER_NAME --network=$NETWORK tester
  fi
fi

EXPECTED="TEST"
TEST=$(docker exec -i $CONTAINER_NAME sh -c "echo -n $EXPECTED | nc server 12345")
IFS=: read message result <<< "$TEST"
RESULT=$(echo "$result" | xargs)

if [ "$RESULT" = "$EXPECTED" ]; then
    echo "Server is working correctly"
else
    echo "Server is NOT working correctly"
fi