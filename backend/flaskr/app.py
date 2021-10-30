from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from flaskr.models import db, setup_db, User, Exercise
from flaskr.database import (
  get_all_users,
  get_exercises_count,
  get_user_data,
  get_exercise_by_user,
  filter_exercise_by_to_date,
  filter_exercise_by_dates,
  filter_exercise_by_from_date,
  is_user_taken,
  save_exercise,
  save_user
)


def create_app(test_config=False):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app, test_config)
    Migrate(app, db)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # return app

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
            is_username_taken = is_user_taken(User, new_username)

            if is_username_taken:
                return 'This user is already taken'

            else:
                user = save_user(User, new_username)

                return jsonify(user)

        except Exception:
            abort(422)

    @app.route('/api/exercise/users', methods=['GET'])
    def retrieve_all_users():
        '''
        GET /api/exercise/users
        returns a json {'users': users} where users is the list of users
        '''
        users = get_all_users(User)

        if len(users) != 0:
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
            user = get_user_data(User, user_uuid)
            is_username_valid = user.get('_id', None)

            if not is_username_valid:
                return 'This user does not exist'

            else:
                exercise = save_exercise(
                  Exercise, new_desc, new_dur, new_date, user_uuid
                )
                print('exercise new', exercise)

                return jsonify(exercise)

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
        exercises_counted = get_exercises_count(Exercise)

        try:
            if not user_id:
                return jsonify({
                  'count': exercises_counted
                })
            elif user_id:
                user = get_user_data(User, user_id)
                exercises_data = get_exercise_by_user(Exercise, user_id)

                if from_date and to_date:
                    exercises_data = filter_exercise_by_dates(
                      Exercise, user_id, from_date, to_date
                    )
                elif from_date:
                    exercises_data = filter_exercise_by_from_date(
                      Exercise, user_id, from_date
                    )
                elif to_date:
                    exercises_data = filter_exercise_by_to_date(
                      Exercise, user_id, to_date
                    )

                if limit:
                    exercises_data = exercises_data[0:limit]

                if len(exercises_data) != 0:
                    return jsonify({
                      '_id': user.get('_id'),
                      'username': user.get('username'),
                      'count': len(exercises_data),
                      'log': exercises_data
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

    return app


if __name__ == '__main__':
    app = create_app(test_config=False)
    app.run(host='0.0.0.0', debug=True)
