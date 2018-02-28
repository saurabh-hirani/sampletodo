''' Todo app config '''
import os

class Config(object):
  ''' Flask config base class '''
  SAMPLETODO_DEBUG = os.getenv('SAMPLETODO_DEBUG', True)
  if SAMPLETODO_DEBUG == 'False':
    SAMPLETODO_DEBUG = False

  SAMPLETODO_HOST = os.getenv('SAMPLETODO_HOST', '127.0.0.1')
  SAMPLETODO_PORT = os.getenv('SAMPLETODO_PORT', 8080)
  SAMPLETODO_USERNAME = os.getenv('SAMPLETODO_USERNAME')
  SAMPLETODO_PASSWORD = os.getenv('SAMPLETODO_PASSWORD')

  DYNAMODB_PORT = os.getenv('DYNAMODB_PORT', 8000)
  DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME', 'sampletodo-table')

class LocalRunConfig(Config):
  ''' Run flask locally '''
  DYNAMODB_ENABLE_LOCAL = True
  DYNAMODB_MOCK = False

  AWS_ACCESS_KEY_ID = 'foo'
  AWS_SECRET_ACCESS_KEY = 'bar'
  AWS_DEFAULT_REGION = 'us-east-1'

  DYNAMODB_HOST = os.getenv('DYNAMODB_HOST', '127.0.0.1')

class TestLocalRunConfig(LocalRunConfig):
  ''' Run flask tests locally '''
  LOGIN_DISABLED = True
  TESTING = True
  DYNAMODB_ENABLE_LOCAL = False
  DYNAMODB_MOCK = True
  DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME', 'SampletodoTesting')

class DockerConfig(Config):
  ''' Run flask via docker cmdline '''
  DYNAMODB_ENABLE_LOCAL = True
  DYNAMODB_MOCK = False

  AWS_ACCESS_KEY_ID = 'foo'
  AWS_SECRET_ACCESS_KEY = 'bar'
  AWS_DEFAULT_REGION = 'us-east-1'

  SAMPLETODO_HOST = os.getenv('SAMPLETODO_HOST', '0.0.0.0')
  DYNAMODB_HOST = os.getenv('DYNAMODB_PORT_8000_TCP_ADDR')
  DYNAMODB_PORT = os.getenv('DYNAMODB_PORT_8000_TCP_PORT')

class DockerComposeConfig(Config):
  ''' Run flask via docker compose '''
  DYNAMODB_ENABLE_LOCAL = True
  DYNAMODB_MOCK = False

  AWS_ACCESS_KEY_ID = 'foo'
  AWS_SECRET_ACCESS_KEY = 'bar'
  AWS_DEFAULT_REGION = 'us-east-1'

  SAMPLETODO_HOST = os.getenv('SAMPLETODO_HOST', '0.0.0.0')
  DYNAMODB_HOST = os.getenv('DYNAMODB_HOST', 'dynamodb-local')
