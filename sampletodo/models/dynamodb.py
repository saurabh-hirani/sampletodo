''' Tasks table in dynamodb '''

import os
import structlog
import json
import time
import uuid
import boto3
import traceback
from boto3.dynamodb.conditions import Attr
from moto import mock_dynamodb2

from sampletodo.version import __version__
import sampletodo.common.utils as utils

class ModelsException(Exception):
  pass

def func_name():
  return traceback.extract_stack(None, 2)[0][2]

class TasksTable(object):
  ''' Store the todo data '''
  mock_dynamodb2 = mock_dynamodb2()

  def _aws_session_assume_role(self):
    ''' Assume AWS role '''
    log_msg = 'aws_session_assume_role'
    try:
      self.log.bind(mechanism='assume_role')
      self.log.info(log_msg,
                    role=self.kwargs['AWS_ROLE_ARN'],
                    session_name=self.kwargs['AWS_ROLE_SESSION_NAME'])

      client = boto3.client('sts')
      response = client.assume_role(RoleArn=self.kwargs['AWS_ROLE_ARN'],
                                    RoleSessionName=self.kwargs['AWS_ROLE_SESSION_NAME'],
                                    DurationSeconds=900)

      aws_access_key_id = response['Credentials']['AccessKeyId']
      aws_secret_access_key = response['Credentials']['SecretAccessKey']
      aws_session_token = response['Credentials']['SessionToken']

      del response['Credentials']['AccessKeyId']
      del response['Credentials']['SecretAccessKey']
      del response['Credentials']['SessionToken']

      self.log.info(log_msg, response=json.dumps(response, default=str))

      session = boto3.Session(aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              aws_session_token=aws_session_token)
    except Exception as ex:
      tb = traceback.format_exc()
      self.log.error(log_msg, status='failed', error=str(ex), traceback=tb)
      self.log = self.log.unbind('mechanism')
      raise ex

    self.log = self.log.unbind('mechanism')
    return session

  def _aws_session_with_keys(self):
    ''' Create AWS session directly '''
    log_msg = 'aws_session_with_keys'
    try:
      self.log.bind(mechanism='keys')
      self.log.info('connection_parameters',
                    aws_access_key_id='***',
                    aws_secret_access_key='***',
                    region_name=self.kwargs['AWS_DEFAULT_REGION'])
      session = boto3.Session(aws_access_key_id=self.kwargs['AWS_ACCESS_KEY_ID'],
                              aws_secret_access_key=self.kwargs['AWS_SECRET_ACCESS_KEY'],
                              region_name=self.kwargs['AWS_DEFAULT_REGION'])
    except Exception as ex:
      tb = traceback.format_exc()
      self.log.error(log_msg, status='failed', error=str(ex), traceback=tb)
      self.log = self.log.unbind('mechanism')
      raise ex

    self.log = self.log.unbind('mechanism')
    return session

  def aws_connect_dynamodb(self):
    ''' Connect to AWS DynamoDB '''
    log_msg = 'connecting_to_dynamodb'
    self.log.info(log_msg, status='started')
    try:
      if self.kwargs['DYNAMODB_ENABLE_LOCAL']:
        self.url = 'http://%s:%s' % (self.kwargs['DYNAMODB_HOST'],
                                     self.kwargs['DYNAMODB_PORT'])
        self.client = self.session.client('dynamodb', endpoint_url=self.url,
                                           region_name=self.kwargs['AWS_DEFAULT_REGION'])
        self.resource = self.session.resource('dynamodb', endpoint_url=self.url,
                                               region_name=self.kwargs['AWS_DEFAULT_REGION'])
      else:
        self.client = self.session.client('dynamodb',
                                           region_name=self.kwargs['AWS_DEFAULT_REGION'])
        self.resource = self.session.resource('dynamodb',
                                               region_name=self.kwargs['AWS_DEFAULT_REGION'])
    except Exception as ex:
      tb = traceback.format_exc()
      self.log.info(log_msg, status='failed', error=str(ex), traceback=tb)
      raise ex

    self.log.info(log_msg, status='done')

  def aws_create_session(self):
    ''' Create AWS session'''
    log_msg = 'creating_boto3_session'
    self.log.info(log_msg, status='started')

    if os.environ['SAMPLETODO_CONFIG_ENV'] == 'TestLocalRunConfig':
      self.session = boto3.Session()
    else:
      try:
        self.session = self._aws_session_with_keys()
      except Exception as ex:
        self.session = self._aws_session_assume_role()

    self.log.info('aws_session_object', session=self.session)
    self.log.info(log_msg, status='done')

  def _table_exists(self):
    ''' Check if a specific table exists '''
    self.log.info('checking_table_exists')

    try:
      response = self.client.list_tables()
    except Exception as ex:
      tb = traceback.format_exc()
      self.log.error('failed_table_exists_error', error=str(ex))
      self.log.error('failed_table_exists_traceback', traceback=tb)
      raise ex

    return self.kwargs['DYNAMODB_TABLE_NAME'] in response['TableNames']

  def _create_table(self):
    ''' Create table '''
    self.log.info('creating_table')
    try:
      response = self.client.create_table(
        TableName=self.kwargs['DYNAMODB_TABLE_NAME'],
        KeySchema=[
          {
            'AttributeName': 'id',
            'KeyType': 'HASH'  #Partition key
          }
        ],
        AttributeDefinitions=[
          {
            'AttributeName': 'id',
            'AttributeType': 'S'
          }
        ],
        ProvisionedThroughput={
          'ReadCapacityUnits': 10,
          'WriteCapacityUnits': 10
        }
      )
    except Exception as ex:
      tb = traceback.format_exc()
      self.log.error('failed_create_table_error', error=str(ex))
      self.log.error('failed_create_table_traceback', traceback=tb)
      raise ex
    return response

  def refresh_aws_connection(self):
    ''' Reconnect AWS assume role '''
    log_msg = 'initializing_aws'
    self.log.info(log_msg, status='started')

    try:
      self.aws_create_session()
    except Exception as ex:
      tb = traceback.format_exc()
      self.log.error('failed_aws_create_session', error=str(ex), traceback=tb)
      raise ex

    try:
      self.aws_connect_dynamodb()
    except Exception as ex:
      tb = traceback.format_exc()
      self.log.error('failed_aws_connect_dynamodb', error=str(ex), traceback=tb)
      raise ex

    if not self._table_exists():
      if self.kwargs['DYNAMODB_MOCK'] or self.kwargs['DYNAMODB_ENABLE_LOCAL']:
        self._create_table()
      else:
        if not self.kwargs['DYNAMODB_ENABLE_LOCAL']:
          err = 'Table does not exist'
          self.log.error('failed_initializing_model', err=err)
          raise ModelsException(err)

    self._table = self.resource.Table(self.kwargs['DYNAMODB_TABLE_NAME'])

    self.log.info(log_msg, status='done')

  def __init__(self, **kwargs):

    self.kwargs = kwargs

    logger = structlog.get_logger()
    self.log = logger.new()
    self.log = self.log.bind(build_version=__version__)

    self.log = self.log.bind(stage='initializing')

    self.log.debug('initializing_model', class_name=self.__class__, kwargs=kwargs)

    if self.kwargs['DYNAMODB_MOCK']:
      self.log.debug('mocking dynamodb')
      self.mock_dynamodb2.start()

    self.refresh_aws_connection()

    self.log = self.log.unbind('stage')

  def put_item(self, item):
    ''' Create item '''
    self.log.debug('put_item', item=item)
    if 'title' not in item:
      err = 'Title not provided'
      self.log.error('failed_put_item', err=err)
      raise ModelsException(err)

    timestamp = int(time.time())

    item['id'] = str(uuid.uuid1())
    item['createdat'] = timestamp
    item['updatedat'] = timestamp
    item['done'] = False

    self.log.debug('put_item', item=item)

    self._table.put_item(Item=item)

    return item

  def get_item_by_id(self, item_id):
    ''' Get item by id '''
    self.log.debug(func_name(), item_id=item_id)
    result = self._table.get_item(Key={'id': item_id})
    self.log.info(func_name(), result=result)
    return result

  def get_item_by_title(self, title):
    ''' Get item by title '''
    self.log.debug(func_name(), title=title)
    result = self._table.scan(
              Select='ALL_ATTRIBUTES',
              FilterExpression=Attr('title').begins_with(title))
    self.log.info(func_name(), result=result)
    return result

  def get_item_by_attr(self, attr_name, attr_value):
    ''' Get item by attr_name == attr_value '''
    self.log.debug(func_name(), attr_name=attr_name, attr_value=attr_value)
    result = self._table.scan(
              Select='ALL_ATTRIBUTES',
              FilterExpression=Attr(attr_name).eq(attr_value))
    self.log.info(func_name(), result=result)
    return result

  def list_items(self):
    ''' Get all items '''
    result = self._table.scan()
    self.log.info(func_name(), result=result)
    return result

  def delete_item(self, item_id):
    ''' Delete item by id '''
    self.log.debug(func_name(), item_id=item_id)
    result = self._table.delete_item(Key={'id': item_id})
    self.log.info(func_name(), result=result)
    return result

  def delete_all_items(self):
    ''' Delete all items '''
    self.log.debug('delete_all_items')

    if self._table_exists():
      result = self._table.scan()
      for item in result['Items']:
        self.log.debug('deleting_item', item_id=item['id'])
        self.delete_item(item['id'])

  def update_item(self, item_id, updated_attrs):
    ''' Update item attrs '''
    self.log.debug(func_name(), item_id=item_id, updated_attrs=updated_attrs)

    item = self.get_item_by_id(item_id)
    if 'Item' not in item:
      err = 'Did not find task'
      self.log.debug(err, item_id=item_id)
      raise ModelsException(err)

    for attr in ['title', 'done']:
      if attr not in updated_attrs:
        updated_attrs[attr] = item['Item'][attr]

    timestamp = int(time.time())

    result = self._table.update_item(
              Key={
                'id': item_id
              },
              ExpressionAttributeValues={
                ':title': updated_attrs['title'],
                ':done': updated_attrs['done'],
                ':updatedat': timestamp,
              },
              UpdateExpression='SET title = :title, '
                               'done = :done, '
                               'updatedat = :updatedat',
              ReturnValues='UPDATED_NEW',
            )
    self.log.info(func_name(), result=result)
    return result
