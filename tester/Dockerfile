FROM ubuntu:latest
RUN apt-get update \
    && apt-get install netcat -y

RUN mkdir -p /tester
WORKDIR /tester/
COPY test.sh .

RUN chmod +x test.sh

ENTRYPOINT ./test.sh