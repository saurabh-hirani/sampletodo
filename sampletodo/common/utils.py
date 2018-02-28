import os
import uuid
import logging
import flask
import boto3
import structlog
from termcolor import colored

def setup_lib_log_levels():
  ''' Setup other libraries log level '''
  logging.getLogger('werkzeug').setLevel(logging.ERROR)
  logging.getLogger('boto3').setLevel(logging.WARNING)
  logging.getLogger('botocore').setLevel(logging.WARNING)
  logging.getLogger('nose').setLevel(logging.WARNING)

# Detailed explanation of this function on
# http://blog.mcpolemic.com/2016/01/18/adding-request-ids-to-flask.html
def generate_request_id(original_id=''):
  ''' Generate request id '''
  if original_id:
    return original_id
  return str(uuid.uuid4())

# Detailed explanation of this function on
# http://blog.mcpolemic.com/2016/01/18/adding-request-ids-to-flask.html
#
# Returns the current request ID or a new one if there is none
# In order of preference:
#  * If we've already created a request ID and stored it in the flask.g context local, use that
#  * If a client has passed in the X-Request-Id header, create a new ID with that prepended
#  * Otherwise, generate a request ID and store it in flask.g.request_id
def request_id():
  ''' Get request id '''
  if getattr(flask.g, 'request_id', None):
    if os.environ['SAMPLETODO_TTY'] == 'True':
      return colored(flask.g.request_id, 'green')
    return flask.g.request_id

  headers = flask.request.headers
  original_request_id = headers.get('X-Request-Id')
  new_uuid = generate_request_id(original_request_id)
  flask.g.request_id = new_uuid

  if os.environ['SAMPLETODO_TTY'] == 'True':
    new_uuid = colored(new_uuid, 'green')

  return new_uuid

class RequestIdFilter(logging.Filter):
  # This is a logging filter that makes the request ID available for use in
  # the logging format. Note that we're checking if we're in a request
  # context, as we may want to log things before Flask is fully loaded.
  def filter(self, record):
    record.request_id = request_id() if flask.has_request_context() else ''
    return True

def _app_namer(_, __, event_dict):
  ''' app namer structlog processor '''
  event_dict['app_name'] = 'sampletodo_web_server'
  return event_dict

# based on the understanding gained by
# https://blog.sneawo.com/blog/2017/07/28/json-logging-in-python/
def setup_structlog(tty=False, logging_level=logging.INFO):
  ''' Setup structlog module '''
  # configure logging module
  logging_config = {
    'version': 1,
    'filters': {
      'request_id': {
        '()': 'sampletodo.utils.RequestIdFilter'
      }
    },
    'disable_existing_loggers': False,
    'loggers': {
      '': {
        'level': logging_level
      }
    }
  }

  logging_config['formatters'] = {}
  logging_config['handlers'] = {}
  logging_config['loggers']['']['handlers'] = []

  if tty:
    logging_config['formatters']['tty'] = {
      '()': structlog.stdlib.ProcessorFormatter,
      'processor': structlog.dev.ConsoleRenderer(colors=True),
      'format': '[%(process)s] [%(pathname)s:%(funcName)s:%(lineno)s] %(request_id)s %(message)s'
    }
    logging_config['handlers']['tty'] = {
      'class': 'logging.StreamHandler',
      'formatter': 'tty',
      'filters': ['request_id']
    }
    logging_config['loggers']['']['handlers'].append('tty')
  else:
    logging_config['formatters']['json'] = {
      '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
      'format': '%(lineno)d %(process)s %(pathname)s %(funcName) %(request_id)s',
    }
    logging_config['handlers']['json'] = {
      'class': 'logging.StreamHandler',
      'formatter': 'json',
      'filters': ['request_id']
    }
    logging_config['loggers']['']['handlers'].append('json')

  logging.config.dictConfig(logging_config)

  # configure structlog
  structlog.configure(
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    processors=[
      _app_namer,
      structlog.stdlib.filter_by_level,
      structlog.stdlib.add_logger_name,
      structlog.stdlib.add_log_level,
      structlog.stdlib.PositionalArgumentsFormatter(),
      structlog.processors.TimeStamper(fmt='iso'),
      structlog.processors.StackInfoRenderer(),
      structlog.processors.format_exc_info,
      structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
  )

def setup_structlog_wrapper():
  ''' setup_structlog wrapper '''
  logging_level = logging.INFO
  if 'SAMPLETODO_DEBUG' in os.environ and os.environ['SAMPLETODO_DEBUG'] == 'True':
    logging_level = logging.DEBUG

  setup_lib_log_levels()

  tty_logging = False
  colored_logging = False

  if 'SAMPLETODO_TTY' not in os.environ:
    os.environ['SAMPLETODO_TTY'] = 'False'

  if os.environ['SAMPLETODO_TTY'] == 'True':
    tty_logging = True

  setup_structlog(tty_logging, logging_level)
