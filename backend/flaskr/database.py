def get_all_users(model):
    users_data = model.query.order_by(model.id).all()
    if len(users_data) > 0:
        users_data = [user.format() for user in users_data]
    return users_data


def get_exercises_count(model):
    data = model.query.count()
    return data


def get_user_data(model, user_id):
    user_data = model.query.filter(model.id == user_id).one_or_none()
    if user_data is not None:
        user_data = user_data.format()
    return user_data


def get_exercise_by_user(model, user_id):
    exercises_data = model.query.filter(
        model.user_uuid == user_id
    ).all()
    if len(exercises_data) > 0:
        exercises_data = [exercise.short() for exercise in exercises_data]
    return exercises_data


def filter_exercise_by_dates(model, user_id, from_date, to_date):
    exercises_data = model.query.filter(
        model.user_uuid == user_id,
        model.exercise_date >= from_date,
        model.exercise_date <= to_date
    ).all()
    if len(exercises_data) > 0:
        exercises_data = [exercise.short() for exercise in exercises_data]
    return exercises_data


def filter_exercise_by_from_date(model, user_id, from_date):
    exercises_data = model.query.filter(
        model.user_uuid == user_id,
        model.exercise_date >= from_date
    ).all()
    if len(exercises_data) > 0:
        exercises_data = [exercise.short() for exercise in exercises_data]
    return exercises_data


def filter_exercise_by_to_date(model, user_id, to_date):
    exercises_data = model.query.filter(
        model.user_uuid == user_id,
        model.exercise_date <= to_date
    ).all()
    if len(exercises_data) > 0:
        exercises_data = [exercise.short() for exercise in exercises_data]
    return exercises_data


def is_user_taken(model, new_username):
    data = model.query.filter(
        model.username == new_username
    ).one_or_none()

    if data is not None:
        data = data.format()
        print('data', data)

    return data


def save_user(model, new_username):
    user = model(username=new_username)
    user.insert()
    return user.format()


def save_exercise(model, new_desc, new_dur, new_date, new_user_uuid):
    exercise = model(
        description=new_desc,
        duration=new_dur,
        exercise_date=new_date,
        user_uuid=new_user_uuid
    )
    exercise.insert()

    return exercise.format()
