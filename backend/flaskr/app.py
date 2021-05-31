import os
import sys
from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from flaskr.models import db, setup_db, User, Exercise
from . import database


def create_app():
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    Migrate(app, db)

    return app


app = create_app()

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


@app.route('/api/exercise/new-user', methods=['POST'])
def add_user():
    '''
    POST /api/exercise/new-user
      it should create a new row in the users table
    returns status a json {user: user} where
      user is an object containing only the newly created user
      or appropriate status code indicating reason for failure
    '''
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

    except Exception:
        abort(422)


@app.route('/api/exercise/users', methods=['GET'])
def retrieve_all_users():
    '''
    GET /api/exercise/users
    returns a json {'users': users} where users is the list of users
    '''
    users_data = database.get_all_users(User)
    users = [user.format() for user in users_data]

    if len(users_data) != 0:
        return jsonify(users)
    else:
        {}

@app.route('/api/exercise/add', methods=['POST'])
def add_exercise():
    '''
    POST /api/exercise/add
      it should create a new row in the exercises table
    returns a json { 'exercise': exercise} where
      exercise is an object containing only the newly created exercise
      or appropriate status code indicating reason for failure
    '''
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
            return 'This user does not exist'

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

    except Exception:
        abort(422)

@app.route('/api/exercise/log', methods=['GET'])
def retrieve_all_exercises():
    '''
    GET /api/exercise/log
    returns a json {'count': count} where count is the number of exercises

    GET /api/exercise/log?user_id&from&to&limit
    returns a json {'user': user, 'log': exercises} where user is the data
      of the user, and log is the list of exercises registered by the user.
      from, to, and limit are optional parameters
    '''
    user_id = request.args.get('user_id', None)
    from_date = request.args.get('from', None)
    to_date = request.args.get('to', None)
    limit = request.args.get('limit', None, type=int)
    exercises_counted = Exercise.query.count()

    try:
        if not user_id:
            return jsonify({
              'count': exercises_counted
            })
        elif user_id:
            user_data = User.query.filter(User.id == user_id).one_or_none()
            user = user_data.format()
            exercises_data = Exercise.query.filter(
              Exercise.user_uuid == user_id
            ).all()

            if from_date and to_date:
                exercises_data = Exercise.query.filter(
                      Exercise.user_uuid == user_id,
                      Exercise.exercise_date >= from_date,
                      Exercise.exercise_date <= to_date
                    ).all()
            elif from_date:
                exercises_data = Exercise.query.filter(
                  Exercise.user_uuid == user_id,
                  Exercise.exercise_date >= from_date
                ).all()
            elif to_date:
                exercises_data = Exercise.query.filter(
                  Exercise.user_uuid == user_id,
                  Exercise.exercise_date <= to_date
                ).all()

            if limit:
                exercises_data = exercises_data[0:limit]

            exercises = [exercise.short() for exercise in exercises_data]

            if len(exercises_data) != 0:
                return jsonify({
                  '_id': user.get('_id'),
                  'username': user.get('username'),
                  'count': len(exercises_data),
                  'log': exercises
                })
            else:
                return {}

    except Exception:
        abort(422)

@app.errorhandler(422)
def unprocessable(error):
    # Error handling for unprocessable entity
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

# return app


# APP = create_app()

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', debug=True)
