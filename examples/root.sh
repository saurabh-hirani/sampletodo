#!/bin/bash -x

echo $0

set -x
curl -v -H "X-Request-Id: $(uuidgen | tr '[:upper:]' '[:lower:]')" http://$SAMPLETODO_HOST:$SAMPLETODO_PORT/
set +x
