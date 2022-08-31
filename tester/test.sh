#!/bin/bash

EXPECTED="TEST"
TEST=$(sh -c "echo -n $EXPECTED | nc server 12345")
IFS=: read message result <<< "$TEST"
RESULT=$(echo "$result" | xargs)

if [ "$RESULT" = "$EXPECTED" ]; then
    echo "Server is working correctly"
else
    echo "Server is NOT working correctly"
fi