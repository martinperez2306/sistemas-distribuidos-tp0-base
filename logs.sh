#!/bin/bash
usage="Debe ingresar el numero de clientes"

if [ $# -eq 0 ]; then
  echo "$usage"
  exit 1    
fi

CLIENTS=$1
LOGS_DIR="logs"

docker logs server >& "$LOGS_DIR/server.txt"

for i in $( seq 1 $CLIENTS )
do
    CLIENT_NAME="client$i"
    docker logs "$CLIENT_NAME" >& "$LOGS_DIR/$CLIENT_NAME.txt"
done