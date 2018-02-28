''' Create app, db and auth objects to be used everywhere else '''

import logging
import logging.config
import os
import uuid
import sys
import argparse
import datetime

from sampletodo.version import __version__ 
import sampletodo.common.utils as utils

from flask import Flask
from flask_httpauth import HTTPBasicAuth

import sampletodo.models.dynamodb as dynamodb

CONFIG_ENV = os.environ.get('SAMPLETODO_CONFIG_ENV', 'LocalRunConfig')

def create_app():
  ''' Create flask app object '''
  obj = Flask(__name__, instance_relative_config=True)
  obj.config.from_object('sampletodo.config.%s' % CONFIG_ENV)
  return obj

def create_db(_app_obj):
  ''' Create DB object '''
  dynamodb_args = {}
  for param, value in _app_obj.config.iteritems():
    if param.startswith('DYNAMODB') or param.startswith('AWS'):
      dynamodb_args[param] = value
  obj = dynamodb.TasksTable(**dynamodb_args)
  return obj

def create_auth():
  ''' Create HTTP auth object '''
  return HTTPBasicAuth()

# do not enable logging while testing locally
if CONFIG_ENV == 'TestLocalRunConfig':
  logger = logging.getLogger()
  logger.disabled = True
else:
  utils.setup_structlog_wrapper()

app = create_app()
db = create_db(app)
auth = create_auth()

from sampletodo import views
