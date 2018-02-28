#!/bin/bash -e

set -x
curl -v -u $SAMPLETODO_USERNAME:$SAMPLETODO_PASSWORD \
     -H "X-Request-Id: $(uuidgen | tr '[:upper:]' '[:lower:]')" \
     -X POST http://$SAMPLETODO_HOST:$SAMPLETODO_PORT/todo/api/v1.0/reconnect-db
set +x
