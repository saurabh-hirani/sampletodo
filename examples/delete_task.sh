#!/bin/bash -e

if [[ $# -ne 1 ]]; then
  echo "Invalid usage"
  echo "usage: $0 task_uuid"
  exit 1
fi

echo "$0 $1"

TASK_UUID=$1

set -x
curl -v -u $SAMPLETODO_USERNAME:$SAMPLETODO_PASSWORD \
     -H "X-Request-Id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
     -X DELETE http://$SAMPLETODO_HOST:$SAMPLETODO_PORT/todo/api/v1.0/tasks/$TASK_UUID
set +x
