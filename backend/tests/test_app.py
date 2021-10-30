import json
import pytest
import flaskr.app
import flaskr.models


@pytest.fixture
def app(mocker):
    mocker.patch("flask_sqlalchemy.SQLAlchemy.create_all", return_value=True)
    mocker.patch("flask_sqlalchemy.SQLAlchemy.init_app", return_value=True)
    mocker.patch("flaskr.app.setup_db", return_value=True)
    flaskr.app.app = flaskr.app.create_app(test_config=True)

    return flaskr.app.app


def test_get_index(client):
    res = client.get("/api/exercise", headers={})
    data = res.data

    assert res.status_code == 200
    assert len(data) > 0


def test_get_users(client, mocker):
    mocker.patch(
        "flaskr.app.get_all_users",
        return_value=[
            {
                "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
                "username": "manuelaM"
            },
            {
                "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d8",
                "username": "manuela M"
            },
            {
                "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d9",
                "username": "manuelaMR"
            }
        ]
    )
    expected_data = [
        {
            "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
            "username": "manuelaM"
        },
        {
            "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d8",
            "username": "manuela M"
        },
        {
            "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d9",
            "username": "manuelaMR"
        }
    ]
    res = client.get("/api/exercise/users", headers={})
    data = json.loads(res.data)

    assert res.status_code == 200
    assert len(data) > 0
    assert data == expected_data


def test_retrieve_all_exercises_count(client, mocker):
    mocker.patch(
        "flaskr.app.get_exercises_count",
        return_value=3
    )
    expected_data = {"count": 3}
    res = client.get("/api/exercise/log", headers={})
    data = json.loads(res.data)

    assert res.status_code == 200
    assert len(data) > 0
    assert data["count"] == expected_data["count"]


def test_get_422_retrieve_all_exercises_by_user_invalid(client, mocker):
    mocker.patch(
        "flaskr.app.get_exercises_count",
        return_value=3
    )
    mocker.patch(
        "flaskr.app.get_user_data",
        return_value=None
    )
    res = client.get(
        "/api/exercise/log?user_id=1ee8efb0-38ac-482d-8bb4-de549f32f98d",
        headers={}
    )
    data = json.loads(res.data)

    assert res.status_code == 422
    assert data["message"] == "Unprocessable"
    assert data["success"] is not True


def test_get_exercise_by_user(client, mocker):
    mocker.patch(
        "flaskr.app.get_exercises_count",
        return_value=3
    )
    mocker.patch(
        "flaskr.app.get_user_data",
        return_value={
            "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
            "username": "manuelaM"
        },
    )
    mocker.patch(
        "flaskr.app.get_exercise_by_user",
        return_value=[
            {
                "description": "my description",
                "duration": "12",
                "date": "Fri Mar 12 2021"
            },
            {
                "description": "my description 2",
                "duration": "13",
                "date": "Sat Mar 13 2021"
            },
            {
                "description": "my description 3",
                "duration": "14",
                "date": "Sun Mar 14 2021"
            }
        ],
    )
    user_id = "91298d0b-66c9-493b-8c1d-a79bcf7838d7"
    expected_user_data = {
        "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
        "username": "manuelaM"
    }
    expected_exercises_data = [
        {
            "description": "my description",
            "duration": "12",
            "date": "Fri Mar 12 2021"
        },
        {
            "description": "my description 2",
            "duration": "13",
            "date": "Sat Mar 13 2021"
        },
        {
            "description": "my description 3",
            "duration": "14",
            "date": "Sun Mar 14 2021"
        }
    ]
    res = client.get(
        f"/api/exercise/log?user_id={user_id}",
        headers={}
    )
    data = json.loads(res.data)

    assert res.status_code == 200
    assert data["count"] == len(expected_exercises_data)
    assert len(data["log"]) > 0
    assert data["_id"] == str(expected_user_data["_id"])
    assert data["username"] == str(expected_user_data["username"])


def test_get_exercise_by_user_with_limit(client, mocker):
    mocker.patch(
        "flaskr.app.get_exercises_count",
        return_value=3
    )
    mocker.patch(
        "flaskr.app.get_user_data",
        return_value={
            "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
            "username": "manuelaM"
        }
    )
    mocker.patch(
        "flaskr.app.get_exercise_by_user",
        return_value=[
            {
                "description": "my description",
                "duration": "12",
                "date": "Fri Mar 12 2021"
            },
            {
                "description": "my description 2",
                "duration": "13",
                "date": "Sat Mar 13 2021"
            },
            {
                "description": "my description 3",
                "duration": "14",
                "date": "Sun Mar 14 2021"
            }
        ],
    )
    expected_user_data = {
        "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
        "username": "manuelaM"
    }

    user_id = "91298d0b-66c9-493b-8c1d-a79bcf7838d7"
    limit = 2
    res = client.get(
        f"/api/exercise/log?user_id={user_id}&limit={limit}",
        headers={}
    )
    data = json.loads(res.data)

    assert res.status_code == 200
    assert data["count"] == limit
    assert len(data["log"]) > 0
    assert data["_id"] == str(expected_user_data["_id"])
    assert data["username"] == str(expected_user_data["username"])


def test_get_exercise_by_user_with_from_date(client, mocker):
    mocker.patch(
        "flaskr.app.get_exercises_count",
        return_value=3
    )
    mocker.patch(
        "flaskr.app.get_user_data",
        return_value={
            "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
            "username": "manuelaM"
        },
    )
    mocker.patch(
        "flaskr.app.get_exercise_by_user",
        return_value=[
            {
                "description": "my description",
                "duration": "12",
                "date": "Fri Mar 12 2021"
            },
            {
                "description": "my description 2",
                "duration": "13",
                "date": "Sat Mar 13 2021"
            },
            {
                "description": "my description 3",
                "duration": "14",
                "date": "Sun Mar 14 2021"
            }
        ]
    )
    mocker.patch(
        "flaskr.app.filter_exercise_by_from_date",
        return_value=[
            {
                "description": "my description 2",
                "duration": "13",
                "date": "Sat Mar 13 2021"
            },
            {
                "description": "my description 3",
                "duration": "14",
                "date": "Sun Mar 14 2021"
            }
        ]
    )
    expected_user_data = {
        "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
        "username": "manuelaM"
    }
    expected_exercises_data = [
        {
            "description": "my description 2",
            "duration": "13",
            "date": "Sat Mar 13 2021"
        },
        {
            "description": "my description 3",
            "duration": "14",
            "date": "Sun Mar 14 2021"
        }
    ]
    user_id = "91298d0b-66c9-493b-8c1d-a79bcf7838d7"
    from_date = "2021-03-13"
    res = client.get(
        f"/api/exercise/log?user_id={user_id}&from={from_date}",
        headers={}
    )
    data = json.loads(res.data)

    assert res.status_code == 200
    assert data["count"] == len(expected_exercises_data)
    assert len(data["log"]) > 0
    assert data["_id"] == str(expected_user_data["_id"])
    assert data["username"] == str(expected_user_data["username"])


def test_get_exercise_by_user_with_to_date(client, mocker):
    mocker.patch(
        "flaskr.app.get_exercises_count",
        return_value=3
    )
    mocker.patch(
        "flaskr.app.get_user_data",
        return_value={
            "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
            "username": "manuelaM"
        },
    )
    mocker.patch(
        "flaskr.app.get_exercise_by_user",
        return_value=[
            {
                "description": "my description",
                "duration": "12",
                "date": "Fri Mar 12 2021"
            },
            {
                "description": "my description 2",
                "duration": "13",
                "date": "Sat Mar 13 2021"
            },
            {
                "description": "my description 3",
                "duration": "14",
                "date": "Sun Mar 14 2021"
            }
        ]
    )
    mocker.patch(
        "flaskr.app.filter_exercise_by_to_date",
        return_value=[
            {
                "description": "my description",
                "duration": "12",
                "date": "Fri Mar 12 2021"
            },
            {
                "description": "my description 2",
                "duration": "13",
                "date": "Sat Mar 13 2021"
            },
        ],
    )
    expected_user_data = {
        "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
        "username": "manuelaM"
    }
    expected_exercises_data = [
        {
            "description": "my description",
            "duration": "12",
            "date": "Fri Mar 12 2021"
        },
        {
            "description": "my description 2",
            "duration": "13",
            "date": "Sat Mar 13 2021"
        }
    ]
    user_id = "91298d0b-66c9-493b-8c1d-a79bcf7838d7"
    to_date = "2021-03-13"
    res = client.get(
        f"/api/exercise/log?user_id={user_id}&to={to_date}",
        headers={}
    )
    data = json.loads(res.data)

    assert res.status_code == 200
    assert data["count"] == len(expected_exercises_data)
    assert len(data["log"]) > 0
    assert data["_id"] == str(expected_user_data["_id"])
    assert data["username"] == str(expected_user_data["username"])


def test_get_exercise_by_user_with_all_filters(client, mocker):
    mocker.patch(
        "flaskr.app.get_exercises_count",
        return_value=3
    )
    mocker.patch(
        "flaskr.app.get_user_data",
        return_value={
            "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
            "username": "manuelaM"
        },
    )
    mocker.patch(
        "flaskr.app.get_exercise_by_user",
        return_value=[
            {
                "description": "my description",
                "duration": "12",
                "date": "Fri Mar 12 2021"
            },
            {
                "description": "my description 2",
                "duration": "13",
                "date": "Sat Mar 13 2021"
            },
            {
                "description": "my description 3",
                "duration": "14",
                "date": "Sun Mar 14 2021"
            }
        ],
    )
    mocker.patch(
        "flaskr.app.filter_exercise_by_dates",
        return_value=[
            {
                "description": "my description",
                "duration": "12",
                "date": "Fri Mar 12 2021"
            },
            {
                "description": "my description 2",
                "duration": "13",
                "date": "Sat Mar 13 2021"
            },
            {
                "description": "my description 3",
                "duration": "14",
                "date": "Sun Mar 14 2021"
            }
        ],
    )
    expected_user_data = {
        "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
        "username": "manuelaM"
    }
    expected_exercises_data = [
        {
            "description": "my description",
            "duration": "12",
            "date": "Fri Mar 12 2021"
        },
        {
            "description": "my description 2",
            "duration": "13",
            "date": "Sat Mar 13 2021"
        },
        {
            "description": "my description 3",
            "duration": "14",
            "date": "Sat Mar 14 2021"
        }
    ]
    user_id = "91298d0b-66c9-493b-8c1d-a79bcf7838d7"
    from_date = "2021-03-12"
    to_date = "2021-03-14"
    limit = 2
    res = client.get(
        f"/api/exercise/log?user_id={user_id}&from={from_date}&to={to_date}\
        &limit={limit}",
        headers={}
    )
    data = json.loads(res.data)
    expected_exercises_data = expected_exercises_data[0:limit]

    assert res.status_code == 200
    assert data["count"] == len(expected_exercises_data)
    assert len(data["log"]) > 0
    assert data["_id"] == str(expected_user_data["_id"])
    assert data["username"] == str(expected_user_data["username"])


def test_create_new_user(client, mocker):
    mocker.patch(
        "flaskr.app.is_user_taken",
        return_value=None
    )
    mocker.patch(
        "flaskr.app.save_user",
        return_value={
            "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
            "username": "manuelaM"
        },
    )
    user_data = {
        "id": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
        "username": "manuelaM"
    }
    res = client.post(
        "/api/exercise/new-user",
        headers={},
        data={"username": "manuelaM"}
    )
    data = json.loads(res.data)

    assert res.status_code == 200
    assert (len(data)) > 0
    assert data["username"] == user_data["username"]
    assert data["_id"] == user_data["id"]


def test_create_new_user_with_username_taken(client, mocker):
    mocker.patch(
        "flaskr.app.is_user_taken",
        return_value={
            "id": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
            "username": "manuelaM"
        }
    )
    res = client.post(
        "/api/exercise/new-user",
        headers={},
        data={"username": "manuelam"}
        )
    data = res.data

    assert res.status_code == 200
    assert data == b"This user is already taken"


def test_422_create_new_user_without_data_as_form(client):
    res = client.post(
        "/api/exercise/new-user",
        headers={},
        json={"username": "manuelam"}
    )
    data = json.loads(res.data)

    assert res.status_code == 422
    assert data["message"] == "Unprocessable"
    assert data["success"] is False


def test_404_create_new_user_with_bad_endpoint(client):
    res = client.post(
        "/movies",
        headers={},
        json={"username": "manuelam"}
    )
    data = json.loads(res.data)

    assert res.status_code == 404
    assert data["message"] == "Not found"
    assert data["success"] is False


def test_create_new_exercise(client, mocker):
    new_exercise = {
        "userId": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
        "exercise_date": "Fri, 15 May 2021 00:00:00 GMT",
        "description": "My exercise",
        "duration": "12"
    }
    mocker.patch(
        "flaskr.app.get_user_data",
        return_value={
            "_id": "91298d0b-66c9-493b-8c1d-a79bcf7838d7",
            "username": "manuelaM"
        }
    )
    mocker.patch(
        "flaskr.app.save_exercise",
        return_value=new_exercise
    )
    res = client.post(
        "/api/exercise/add",
        headers={},
        data=new_exercise
    )
    data = json.loads(res.data)

    assert res.status_code == 200
    assert len(data) >= 0
    assert data["description"] == new_exercise["description"]


def test_create_new_exercise_without_valid_username(client, mocker):
    new_exercise = {
        "userId": "912",
        "exercise_date": "Fri, 15 May 2021 00:00:00 GMT",
        "description": "My exercise",
        "duration": "12"
    }
    mocker.patch(
        "flaskr.app.get_user_data",
        return_value=None
    )
    res = client.post(
        "/api/exercise/add",
        headers={},
        data=new_exercise
        )
    data = json.loads(res.data)

    assert res.status_code == 422
    assert data["message"] == "Unprocessable"
    assert data["success"] is False


def test_422_create_new_exercise_without_data_as_form(client):
    new_exercise = {
        "userId": "912",
        "exercise_date": "Fri, 15 May 2021 00:00:00 GMT",
        "description": "My exercise",
        "duration": "12"
    }
    res = client.post(
        "/api/exercise/add",
        headers={},
        json=new_exercise
    )
    data = json.loads(res.data)

    assert res.status_code == 422
    assert data["message"] == "Unprocessable"
    assert data["success"] is False
