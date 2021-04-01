# import os
import sys
# import json
from flask import Flask, request, abort, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy import exc
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, setup_db, User, Exercise


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    migrate = Migrate(app, db)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
          'Access-Control-Allow-Headers', 'Content-Type,Authorization,true'
        )
        response.headers.add(
          'Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS'
        )
        return response

    # ROUTES
    @app.route('/api/exercise')
    def index():
        return 'This is the default index of Exercise Tracker Api Project.'

    '''
    POST /api/exercise/new-user
      it should create a new row in the users table
    returns status a json {user: user} where
      user is an object containing only the newly created user
      or appropriate status code indicating reason for failure
    '''
    @app.route('/api/exercise/new-user', methods=['POST'])
    def add_user():
        new_username = request.form.get('username', None)

        try:
            is_username_taken = User.query.filter(
              User.username == new_username
            ).one_or_none()

            if is_username_taken:
                return 'This user is already taken'

            else:
                user = User(username=new_username)
                user.insert()

                return jsonify({
                  'username': user.username,
                  '_id': user.id
                })

        except Exception as e:
            print(sys.exc_info(), e)
            abort(422)

    '''
    GET /api/exercise/users
    returns a json {'users': users} where users is the list of users
    '''
    @app.route('/api/exercise/users', methods=['GET'])
    def retrieve_all_users():
        users_data = User.query.order_by(User.id).all()
        users = [user.format() for user in users_data]

        if len(users_data):
            return jsonify({
              'users': users
            })
        else:
            abort(404)

        '''
    POST /api/exercise/add
      it should create a new row in the exercises table
    returns a json { 'exercise': exercise} where
      exercise is an object containing only the newly created exercise
      or appropriate status code indicating reason for failure
    '''
    @app.route('/api/exercise/add', methods=['POST'])
    def add_exercise():
        user_uuid = request.form.get('userId', None)
        new_desc = request.form.get('description', None)
        new_dur = request.form.get('duration', None)
        new_date = request.form.get('date', None)

        try:
            user = User.query.filter(
              User.id == user_uuid
            ).one_or_none().format()
            is_username_valid = user.get('_id', None)

            if not is_username_valid:
                return 'This user does not exists'

            else:
                exercise = Exercise(
                  description=new_desc,
                  duration=new_dur,
                  exercise_date=new_date
                )
                exercise.user_uuid = user_uuid
                exercise.insert()

                return jsonify({
                  'user_uuid': exercise.user_uuid,
                  'id': exercise.id,
                  'description': exercise.description,
                  'duration': exercise.duration,
                  'date': exercise.exercise_date
                })

        except Exception as e:
            print(sys.exc_info(), e)
            abort(422)

    '''
    GET /api/exercise/log
    returns a json {'count': count} where count is the number of exercises

    GET /api/exercise/log?user_id&from&to&limit
    returns a json {'user': user, 'log': exercises} where user is the data of
      the user, and log is the list of exercises registered by the user.
      from, to, and limit are optional parameters
    '''
    @app.route('/api/exercise/log', methods=['GET'])
    def retrieve_all_exercises():
        user_id = request.args.get('user_id', None)
        from_date = request.args.get('from', None)
        to_date = request.args.get('to', None)
        limit = request.args.get('limit', None, type=int)

        try:
            if not user_id:
                exercises_counted = Exercise.query.count()

                return jsonify({
                  'count': exercises_counted
                })
            elif user_id:
                user_data = User.query.filter(User.id == user_id).one_or_none()
                user = user_data.format()
                exercises_data = Exercise.query.filter(
                  Exercise.user_uuid == user_id
                ).all()

                if from_date:
                    exercises_data = Exercise.query.filter(
                      Exercise.user_uuid == user_id,
                      Exercise.exercise_date >= from_date
                    ).all()
                    if to_date:
                        exercises_data = Exercise.query.filter(
                          Exercise.exercise_date <= to_date,
                          Exercise.exercise_date >= from_date,
                          Exercise.exercise_date <= to_date
                        ).all()

                if to_date:
                    exercises_data = Exercise.query.filter(
                      Exercise.user_uuid == user_id,
                      Exercise.exercise_date <= to_date
                    ).all()
                    if from_date:
                        exercises_data = Exercise.query.filter(
                          Exercise.exercise_date <= to_date,
                          Exercise.exercise_date >= from_date,
                          Exercise.exercise_date <= to_date
                        ).all()

                exercises = [exercise.short() for exercise in exercises_data]
                if limit:
                    exercises_data = exercises[0:limit]

                if len(exercises_data):
                    return jsonify({
                      'user': user,
                      'log': [exercises]
                    })
                else:
                    abort(404)

        except Exception as e:
            print(sys.exc_info(), e)
            abort(422)

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
