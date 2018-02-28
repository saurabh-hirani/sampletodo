#!/bin/bash -e

set -x
curl -v -u "${SAMPLETODO_USERNAME}123:${SAMPLETODO_PASSWORD}123" \
    -H "X-Request-Id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
     http://$SAMPLETODO_HOST:$SAMPLETODO_PORT/todo/api/v1.0/tasks
set +x
