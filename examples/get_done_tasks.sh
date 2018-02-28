#!/bin/bash -e

echo $0

set -x
curl -v -u $SAMPLETODO_USERNAME:$SAMPLETODO_PASSWORD \
     -H "X-Request-Id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
     http://$SAMPLETODO_HOST:$SAMPLETODO_PORT/todo/api/v1.0/tasks/status/done
set +x
