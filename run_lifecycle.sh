#!/bin/bash

cd examples
SAMPLETODO_HOST=localhost \
SAMPLETODO_PORT=8080 \
SAMPLETODO_USERNAME=testuser \
SAMPLETODO_PASSWORD=testuser \
./lifecycle.sh 2>&1
cd -
