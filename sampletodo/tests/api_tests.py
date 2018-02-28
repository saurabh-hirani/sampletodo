''' Unit tests for the app '''

import os
import base64
import sys
import json
import inspect
import unittest

os.environ['SAMPLETODO_CONFIG_ENV'] = 'TestLocalRunConfig'

from sampletodo import app, auth
from sampletodo import views

@auth.verify_password
def verify_password(user, password):
  ''' Overwrite the password check for unittesting'''
  return True

class JustodoitTestCase(unittest.TestCase):
  ''' Test case class '''
  def setUp(self):
    ''' set up the test environment '''
    app.config['SAMPLETODO_CONFIG_ENV'] = 'TestLocalRunConfig'
    self.client = app.test_client()

    self.content_type_header = {
      'Content-Type': 'application/json'
    }

  def test_get_health(self):
    ''' Test health '''
    url = '/todo/api/v1.0/health'
    response = self.client.open(url, method='GET')
    assert response.status_code == 200

  def test_get_build_version(self):
    ''' Test build_version '''
    url = '/todo/api/v1.0/build_version'
    response = self.client.open(url, method='GET')
    assert response.status_code == 200

  def _delete_all_tasks(self):
    ''' Wrapper for task deletion '''
    url = '/todo/api/v1.0/tasks'

    response = self.client.open(url, method='DELETE')
    return response

  def test_delete_all_tasks(self):
    ''' Test deletion of all tasks '''
    response = self._delete_all_tasks()
    assert response.status_code == 200

  def _get_all_tasks(self):
    ''' Test getting all tasks '''
    url = '/todo/api/v1.0/tasks'

    response = self.client.open(url, method='GET')
    return response

  def test_get_all_tasks(self):
    ''' Test getting all tasks '''
    response = self._get_all_tasks()
    assert response.status_code == 200

  def _create_task(self, task_name):
    ''' Wrapper for task creation '''
    url = '/todo/api/v1.0/tasks'

    headers = {}
    headers.update(self.content_type_header)

    data = json.dumps({'title': task_name})

    response = self.client.open(url, method='POST', data=data, headers=headers)
    return response

  def test_create_task(self):
    ''' Test task creation '''
    func_name = inspect.stack()[0][3]
    task_name = 'function-%s' % func_name
    response = self._create_task(task_name)
    assert response.status_code == 201

  def _get_task_by_id(self, task_id): 
    ''' Wrapper for getting task by id '''
    url = '/todo/api/v1.0/tasks/%s' % task_id
    response = self.client.open(url, method='GET')
    return response

  def test_get_task_by_id(self):
    ''' Test getting a task by id '''
    # create a task
    func_name = inspect.stack()[0][3]
    task_name = 'function-%s' % func_name
    response = self._create_task(task_name)
    response_ds = json.loads(response.data)
    task_id = response_ds['task']['id']

    # try to query the tasks database by that id
    response = self._get_task_by_id(task_id)
    response_ds = json.loads(response.data)

    # verify the task database response
    assert response.status_code == 200
    assert response_ds['task']['id'] == task_id

  def _update_task_attr(self, task_id, attr_name, attr_value):
    ''' Wrapper for updating task attribute '''
    url = '/todo/api/v1.0/tasks/%s' % task_id
    headers = {}
    headers.update(self.content_type_header)
    data = json.dumps({attr_name: attr_value})
    response = self.client.open(url, method='PUT', data=data, headers=headers)
    return response

  def test_update_task_title(self):
    ''' Test updating task title '''
    # create a task
    func_name = inspect.stack()[0][3]
    task_name = 'function-%s' % func_name
    response = self._create_task(task_name)
    response_ds = json.loads(response.data)
    task_id = response_ds['task']['id']

    # update the task title 
    updated_task_title = task_name + '-updated'
    response = self._update_task_attr(task_id, 'title', updated_task_title)
    response_ds = json.loads(response.data)

    # verify the title updation response
    assert response.status_code == 200
    assert response_ds['task']['title'] == updated_task_title

  def test_update_task_status(self):
    ''' Test updating task title '''
    # create task_1
    func_name = inspect.stack()[0][3]
    task_1_name = 'function-%s-1' % func_name
    response = self._create_task(task_1_name)
    response_ds = json.loads(response.data)
    task_1_id = response_ds['task']['id']

    # create task_2
    task_2_name = 'function-%s-2' % func_name
    response = self._create_task(task_2_name)
    response_ds = json.loads(response.data)
    task_2_id = response_ds['task']['id']

    # update the task_1 status
    response = self._update_task_attr(task_1_id, 'done', True)
    response_ds = json.loads(response.data)

    # verify the title updation response
    assert response.status_code == 200
    assert response_ds['task']['done'] == True

    # get all tasks
    response = self._get_all_tasks()
    response_ds = json.loads(response.data)

    # get all pending tasks
    url = '/todo/api/v1.0/tasks/status/pending'
    response = self.client.open(url, method='GET')
    response_ds = json.loads(response.data)

    assert response.status_code == 200
    assert len(response_ds) == 1
    assert response_ds['tasks'][0]['title'] == task_2_name

    # get all done tasks
    url = '/todo/api/v1.0/tasks/status/done'
    response = self.client.open(url, method='GET')
    response_ds = json.loads(response.data)

    assert response.status_code == 200
    assert len(response_ds) == 1
    assert response_ds['tasks'][0]['title'] == task_1_name

  def test_delete_task(self):
    ''' Test task deletion '''
    # create task
    func_name = inspect.stack()[0][3]
    task_name = 'function-%s' % func_name
    response = self._create_task(task_name)
    response_ds = json.loads(response.data)
    task_id = response_ds['task']['id']

    # delete task
    url = '/todo/api/v1.0/tasks/%s' % task_id
    response = self.client.open(url, method='DELETE')
    assert response.status_code == 200

  def tearDown(self):
    ''' tear down the test environment '''
    self._delete_all_tasks()

if __name__ == '__main__':
  unittest.main()
