#!/bin/bash -e

echo "#########################"

./delete_all_tasks.sh

echo "#########################"

./root.sh

echo "#########################"

./health.sh

echo "#########################"

./build_version.sh

echo "#########################"

echo "./get_all_tasks.sh" # can't echo program name inside file because it's output is parsed by ./get_all_uuids.sh

./get_all_tasks.sh

echo "#########################"

./create_task.sh 'Read a book'

echo "#########################"

./create_task.sh 'Read another book'

echo "#########################"

./create_task.sh 'Read one more book'

echo "#########################"

echo "./get_all_tasks.sh" # can't echo program name inside file because it's output is parsed by ./get_all_uuids.sh

./get_all_tasks.sh

echo "#########################"

./get_task_by_id.sh $(./get_all_uuids.sh | head -1)

echo "#########################"

./get_task_by_id.sh $(./get_all_uuids.sh | tail -1)


echo "#########################"

./update_task_title.sh $(./get_all_uuids.sh | head -1) updated_title

echo "#########################"

./mark_task_done.sh $(./get_all_uuids.sh | head -1)

echo "#########################"

./get_task_by_id.sh $(./get_all_uuids.sh | head -1)

echo "#########################"

./get_unauthorized_access.sh

echo "#########################"

./delete_task.sh $(./get_all_uuids.sh | head -1)

echo "#########################"

./delete_all_tasks.sh

