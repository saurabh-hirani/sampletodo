#!/bin/bash -e

if [[ $# -ne 2 ]]; then
  echo "Invalid usage"
  echo "usage: $0 task_uuid new_title"
  exit 1
fi

echo "$0 $1 $2"

TASK_UUID=$1
NEW_TITLE=$2

set -x
curl -v -u $SAMPLETODO_USERNAME:$SAMPLETODO_PASSWORD  \
     -H "Content-Type: application/json" -X PUT \
     -d "{\"title\": \"$NEW_TITLE\"}" http://$SAMPLETODO_HOST:$SAMPLETODO_PORT/todo/api/v1.0/tasks/$TASK_UUID
set +x
