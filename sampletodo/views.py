''' Sample flask todo app '''

import os
import json
import structlog
import traceback
import flask
from flask import jsonify, abort, request, make_response, url_for

from sampletodo.models.dynamodb import ModelsException
from sampletodo import app, db, auth
from sampletodo.version import __version__

logger = structlog.get_logger()
log = logger.new()
log = log.bind(build_version=__version__)

@app.errorhandler(Exception)
def exceptions(e):
  ''' Handle flask exceptions '''
  tb = traceback.format_exc()
  log.error('exception', traceback=tb)
  http_code = 500
  return make_response(jsonify({'error': 'internal_server_error'}), http_code)

@app.after_request
def after_request(response):
  ''' Handle flask response logging '''
  log_method = log.info

  if not str(response.status_code).startswith('20'):
    log_method = log.error
    log_method('response', response_status='error', 
               response_headers=response.headers,
               response_status_code=response.status_code)
  else:
    log_method('response', response_status='success', 
               response_headers=response.headers,
               response_status_code=response.status_code)

  if getattr(flask.g, 'request_id', None):
    if response.headers['Content-Type'] != 'application/json':
      response_data = json.loads(response.get_data())
      response_data['request_id'] = flask.g.request_id
      response.set_data(json.dumps(response_data))

  if 'SAMPLETODO_TTY' in os.environ and os.environ['SAMPLETODO_TTY'] == 'True':
    print("==========================================================")

  return response

@app.before_request
def before_request():
  ''' Handle flask request logging '''
  log.info('request',
           request_remote_addr=request.remote_addr,
           request_method=request.method,
           request_scheme=request.scheme,
           request_full_path=request.full_path)

@auth.get_password
def get_password(username):
  ''' Return users password '''
  if 'SAMPLETODO_USERNAME' not in os.environ or \
     'SAMPLETODO_PASSWORD' not in os.environ:
    return None

  if username == os.environ.get('SAMPLETODO_USERNAME'):
    return os.environ.get('SAMPLETODO_PASSWORD')

  return None

@auth.error_handler
def unauthorized():
  ''' Unauthorized function handler '''
  # return 403 instead of 401 to prevent browsers from displaying the default auth dialog
  http_code = 403
  err = 'unauthorized_access'
  log.error(err)
  return make_response(jsonify({'error': err}), http_code)

@app.errorhandler(400)
def bad_request(err):
  ''' Page Not found handler '''
  http_code = 400
  log.error('bad_request', error=str(err), http_code=http_code)
  response = jsonify(http_code=http_code, text=str(err))
  response.status_code = http_code
  return response

@app.errorhandler(404)
def server_not_found(err):
  ''' 404 handler '''
  http_code = 404
  log.error('server_not_found', error=str(err), http_code=http_code)
  response = jsonify(http_code=http_code, text=str(err))
  response.status_code = http_code
  return response

@app.route('/todo/api/v1.0/reconnect-db', methods=['POST'])
@auth.login_required
def reconnect_db():
  ''' Add task to todo list '''
  log.info('recreating_db_connection')
  result = db.refresh_aws_connection()
  return jsonify({'status': 'done'}), 200

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
@auth.login_required
def get_tasks():
  ''' Get list of tasks '''
  result = db.list_items()

  if 'Items' not in result:
    return jsonify({'tasks': []})

  return jsonify({'tasks': result['Items']})

@app.route('/todo/api/v1.0/tasks/status/<string:task_status>', methods=['GET'])
@auth.login_required
def get_tasks_by_status(task_status):
  ''' Get tasks by done status '''
  if task_status != 'pending' and task_status != 'done':
    return bad_request('Invalid task status - %s' % task_status)

  attr_value = False if task_status == 'pending' else True

  result = db.get_item_by_attr('done', attr_value )

  if 'Items' not in result:
    return jsonify({'tasks': []})

  return jsonify({'tasks': result['Items']})

@app.route('/todo/api/v1.0/tasks/<string:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id):
  ''' Return task from todo list '''
  result = db.get_item_by_id(task_id)

  if 'Item' not in result:
    return jsonify({'task': {}})

  return jsonify({'task': result['Item']})

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
@auth.login_required
def create_task():
  ''' Add task to todo list '''
  if not request.json:
    abort(400)

  try:
    result = db.put_item(request.json)
  except ModelsException as ex:
    return bad_request(str(ex))

  return jsonify({'task': result}), 201

@app.route('/todo/api/v1.0/tasks/<string:task_id>', methods=['PUT'])
@auth.login_required
def update_task(task_id):
  ''' Update task from todo list '''
  if not request.json:
    abort(400)

  try:
    result = db.update_item(task_id, request.json)
  except ModelsException as ex:
    return bad_request(str(ex))

  return jsonify({'task': result['Attributes']})

@app.route('/todo/api/v1.0/tasks/<string:task_id>', methods=['DELETE'])
@auth.login_required
def delete_task(task_id):
  ''' Delete task '''
  try:
    db.delete_item(task_id)
  except ModelsException as ex:
    return bad_request(str(ex))

  return jsonify({'id': task_id, 'deleted': True})

@app.route('/todo/api/v1.0/tasks', methods=['DELETE'])
@auth.login_required
def delete_all_tasks():
  ''' Delete all tasks '''
  try:
    db.delete_all_items()
  except ModelsException as ex:
    return bad_request(str(ex))

  return jsonify({'deleted': True})

@app.route('/', methods=['GET'])
def index():
  ''' Index url '''
  ds = {
    url_for('health'): url_for('health', _external=True),
    url_for('build_version'): url_for('build_version', _external=True),
  }
  return jsonify(ds)

@app.route('/todo/api/v1.0/health', methods=['GET'])
def health():
  ''' Basic health test '''
  return jsonify({'status': 'good'})

@app.route('/todo/api/v1.0/build_version', methods=['GET'])
def build_version():
  ''' Return build_version '''
  return jsonify({'build_version': '%s' % __version__})
