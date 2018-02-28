#!/bin/bash -e


if [[ $# -ne 1 ]]; then
  echo "Invalid usage"
  echo "usage: $0 task_name"
  exit 1
fi

TITLE=$1

echo "$0 $TITLE"

set -x
curl -v -u $SAMPLETODO_USERNAME:$SAMPLETODO_PASSWORD \
    -H "X-Request-Id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
    -H "Content-Type: application/json" -X POST \
    -d "{\"title\":\"$1\"}" http://$SAMPLETODO_HOST:$SAMPLETODO_PORT/todo/api/v1.0/tasks
set +x
