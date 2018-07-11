#!/bin/bash

get_abs_filename() {
  echo "$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
}

DOCKER_DIR=`dirname $0`
PROJECT_ROOT=$(get_abs_filename "$( dirname $DOCKER_DIR )")
docker run --runtime=nvidia -d -v $PROJECT_ROOT:/Finetune finetune
