#!/bin/bash -e

./get_all_tasks.sh 2>/dev/null | jq -r '.tasks | .[] | .id'
