import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Exercise, User


class ExerciseTrackerTestCase(unittest.TestCase):
    # This class represents the Exercise Tracker test case

    def setUp(self):
        # Define test variables and initialize app.
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "exercise-tracker_test"
        setup_db(self.app)

        self.new_user = {
          "username": "manuelar"
        }

        self.new_exercise = {
          "userId": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
          "exercise_date": "Fri, 15 May 2020 00:00:00 GMT",
          "description": "My exercise",
          "duration": "12"
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        # Executed after reach test
        pass

    # Tests for successful operation and for expected errors.

    def test_get_users(self):
        res = self.client().get('/api/exercise/users', headers={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))

    def test_get_exercise_count(self):
        res = self.client().get('/api/exercise/log', headers={})
        data = json.loads(res.data)
        exercise_count = Exercise.query.count()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['count'], exercise_count)

    def test_get_422_exercise_by_user_invalid(self):
        res = self.client().get(
          '/api/exercise/log?user_id=1ee8efb0-38ac-482d-8bb4-de549f32f98d',
          headers={}
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'Unprocessable')
        self.assertEqual(data['success'], False)

    def test_get_exercise_by_user(self):
        user_id = '91298d0b-66c9-493b-8c1d-a79bcf7838d7'
        res = self.client().get(
          f'/api/exercise/log?user_id={user_id}',
          headers={}
        )
        data = json.loads(res.data)
        exercises_data = Exercise.query.filter(
          Exercise.user_uuid == user_id
        ).all()
        user_data = User.query.filter(
          User.id == user_id
        ).one_or_none().format()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['count'], len(exercises_data))
        self.assertTrue(len(data['log']))
        self.assertEqual(data['_id'], str(user_data['_id']))
        self.assertEqual(data['username'], str(user_data['username']))

    def test_get_exercise_by_user_with_limit(self):
        user_id = '91298d0b-66c9-493b-8c1d-a79bcf7838d7'
        limit = 2
        res = self.client().get(
          f'/api/exercise/log?user_id={user_id}&limit={limit}',
          headers={}
        )
        data = json.loads(res.data)
        user_data = User.query.filter(
          User.id == user_id
        ).one_or_none().format()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['count'], limit)
        self.assertTrue(len(data['log']))
        self.assertEqual(data['_id'], str(user_data['_id']))
        self.assertEqual(data['username'], str(user_data['username']))

    def test_get_exercise_by_user_with_from_date(self):
        user_id = '91298d0b-66c9-493b-8c1d-a79bcf7838d7'
        from_date = '2021-04-11'
        res = self.client().get(
          f'/api/exercise/log?user_id={user_id}&from={from_date}',
          headers={}
        )
        data = json.loads(res.data)
        user_data = User.query.filter(
          User.id == user_id
        ).one_or_none().format()
        exercises_data = Exercise.query.filter(
          Exercise.user_uuid == user_id,
          Exercise.exercise_date >= from_date
        ).all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['count'], len(exercises_data))
        self.assertTrue(len(data['log']))
        self.assertEqual(data['_id'], str(user_data['_id']))
        self.assertEqual(data['username'], str(user_data['username']))

    def test_get_exercise_by_user_with_to_date(self):
        user_id = '91298d0b-66c9-493b-8c1d-a79bcf7838d7'
        to_date = '2021-04-10'
        res = self.client().get(
          f'/api/exercise/log?user_id={user_id}&to={to_date}',
          headers={}
        )
        data = json.loads(res.data)
        user_data = User.query.filter(
          User.id == user_id
        ).one_or_none().format()
        exercises_data = Exercise.query.filter(
          Exercise.user_uuid == user_id,
          Exercise.exercise_date <= to_date
        ).all()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['count'], len(exercises_data))
        self.assertTrue(len(data['log']))
        self.assertEqual(data['_id'], str(user_data['_id']))
        self.assertEqual(data['username'], str(user_data['username']))

    def test_get_exercise_by_user_with_all_filters(self):
        user_id = '91298d0b-66c9-493b-8c1d-a79bcf7838d7'
        from_date = '2021-04-10'
        to_date = '2021-04-11'
        limit = 2
        res = self.client().get(
          f'/api/exercise/log?user_id={user_id}&from={from_date}&to={to_date}\
            &limit={limit}',
          headers={}
        )
        data = json.loads(res.data)
        user_data = User.query.filter(
          User.id == user_id
        ).one_or_none().format()
        exercises_data = Exercise.query.filter(
          Exercise.user_uuid == user_id,
          Exercise.exercise_date >= from_date,
          Exercise.exercise_date <= to_date
        ).all()
        exercises_data = exercises_data[0:limit]

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['count'], len(exercises_data))
        self.assertTrue(len(data['log']))
        self.assertEqual(data['_id'], str(user_data['_id']))
        self.assertEqual(data['username'], str(user_data['username']))

    def test_create_new_user(self):
        res = self.client().post(
          '/api/exercise/new-user',
          headers={},
          data=self.new_user
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertEqual(data['username'], self.new_user['username'])

    def test_create_new_user_with_username_taken(self):
        res = self.client().post(
            '/api/exercise/new-user',
            headers={},
            data={'username': 'manuelam'}
          )
        data = res.data

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data, b'This user is already taken')

    def test_422_create_new_user_without_data_as_form(self):
        res = self.client().post(
          '/api/exercise/new-user',
          headers={},
          json=self.new_user
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'Unprocessable')
        self.assertEqual(data['success'], False)

    def test_404_create_new_user_with_bad_endpoint(self):
        res = self.client().post(
          '/movies',
          headers={},
          json=self.new_user
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['message'], 'Not found')
        self.assertEqual(data['success'], False)

    def test_create_new_exercise(self):
        res = self.client().post(
          '/api/exercise/add',
          headers={},
          data=self.new_exercise
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data))
        self.assertEqual(data['description'], self.new_exercise['description'])

    def test_create_new_user_without_valid_username(self):
        new_exercise = {
          "userId": "912",
          "exercise_date": "Fri, 15 May 2021 00:00:00 GMT",
          "description": "My exercise",
          "duration": "12"
        }
        res = self.client().post(
            '/api/exercise/add',
            headers={},
            data=new_exercise
          )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'Unprocessable')
        self.assertEqual(data['success'], False)

    def test_422_create_new_user_without_data_as_form(self):
        res = self.client().post(
          '/api/exercise/add',
          headers={},
          json=self.new_exercise
        )
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'Unprocessable')
        self.assertEqual(data['success'], False)


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
