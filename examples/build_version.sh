#!/bin/bash -e

echo $0

set -x
curl -v http://$SAMPLETODO_HOST:$SAMPLETODO_PORT/todo/api/v1.0/build_version
set +x
