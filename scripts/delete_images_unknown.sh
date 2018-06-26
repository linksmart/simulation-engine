#!/usr/bin/env bash
#set -e

docker rmi -f $(docker images | grep "^<none>" | awk "{print $3}")