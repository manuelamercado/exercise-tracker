import os
import sys
import json
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, setup_db, User

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  migrate = Migrate(app, db)
  CORS(app, resources={r"/*": {"origins": "*"}})

  # CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  ## ROUTES
  @app.route('/api/exercise')
  def index():
    return 'This is the default index of Exercise Tracker Api Project.'

  '''
  POST /api/exercise/new-user
    it should create a new row in the users table
  returns status code 200 and json {'success': True, 'users': user} where users is an array containing only the newly created user
    or appropriate status code indicating reason for failure
  '''
  @app.route('/api/exercise/new-user', methods=['POST'])
  def add_user():
    # body = request.get_json()
    # new_username = body.get('username', None)
    new_username = request.form.get('username', None)

    try:
      is_username_taken = User.query.filter(User.username == new_username).one_or_none()

      if is_username_taken:
        return 'This user is already taken'

      else:
        user = User(username=new_username)
        user.insert()

        return jsonify({
          'username': user.username,
          'id': user.id
        })

    except:
      print(sys.exc_info())
      abort(422)

  ## Error Handling
  '''
  Error handling for unprocessable entity
  '''
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False, 
      'error': 422,
      'message': 'Unprocessable'
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False, 
      'error': 400,
      'message': 'Bad request'
      }), 400
  '''
  Error handler for 404
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False, 
      'error': 404,
      'message': 'Not found'
      }), 404

  @app.errorhandler(401)
  def not_authorized(error):
    return jsonify({
      'success': False, 
      'error': 401,
      'message': 'Not authorized'
      }), 401

  @app.errorhandler(403)
  def not_found_permission(error):
    return jsonify({
      'success': False, 
      'error': 403,
      'message': 'Do not have permissions'
      }), 403

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False, 
      'error': 405,
      'message': 'Method not allowed'
      }), 405

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      'success': False, 
      'error': 500,
      'message': 'Server error'
      }), 500

  return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', debug=True)
