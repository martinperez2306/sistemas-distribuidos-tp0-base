#!/bin/bash
usage="${create_compose} [-h] [-d] [-f] [-s] -- 

where:
    -h, --help
        Show this help text
    -p, --print
        Don't do anything, just print the result of the variable expansion(s)
    -f, --file
        Specify a file to read variables from
    -s, --silent
        Don't print warning messages (for example if no variables are found)

examples:
    VAR1=Something VAR2=1.2.3 ${PROGNAME} test.txt 
    ${PROGNAME} test.txt -f my-variables.txt
    ${PROGNAME} test.txt -f my-variables.txt > new-test.txt"

if [ $# -eq 0 ]; then
  echo "$usage"
  exit 1    
fi

CLIENTS=$1
BASE_TEMPLATE="create_compose/base_template.yaml"
CLIENTS_TEMPLATE="create_compose/clients_template.yaml"
NETWORK_TEMPLATE="create_compose/network_template.yaml"
OUTPUT="docker-compose-dev.yaml"

cat /dev/null > $OUTPUT
cat $BASE_TEMPLATE >> $OUTPUT
echo -e "\n" >> $OUTPUT

for i in $( seq 1 $CLIENTS )
do
    CLIENT_SERVICE="CLIENT_SERVICE"
    CONTAINER_NAME="CONTAINER_NAME"
    CLIENT_NAME="client$i"
    CLI_ID="CLIENT_ID"
    CLIENT_ID=$i
    cat $CLIENTS_TEMPLATE | sed -r "s/$CLIENT_SERVICE/$CLIENT_NAME/g" | sed -r "s/$CONTAINER_NAME/$CLIENT_NAME/g" | sed -r "s/$CLI_ID/$CLIENT_ID/g" >> $OUTPUT
    echo -e "\n" >> $OUTPUT
done

cat $NETWORK_TEMPLATE >> $OUTPUT