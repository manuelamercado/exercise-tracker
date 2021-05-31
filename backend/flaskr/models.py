import os
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
  Column, String, Integer, DateTime, ForeignKey, create_engine
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask_sqlalchemy import SQLAlchemy
import json
import uuid

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app):
    app.config.from_object('config')
    app.app_context().push()
    db.app = app
    db.init_app(app)
    db.create_all()


'''
User
Entity for person that tracks exercises
'''


class User(db.Model):
    __tablename__ = 'User'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, nullable=False)

    def __init__(self, id, username):
        self.id = id
        self.username = username

    def format(self):
        return {
          '_id': self.id,
          'username': self.username,
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        # myparent.children.remove(somechild)
        db.session.delete(self)
        db.session.commit()


'''
Exercise
Entity for exercise that tracks users exercises
'''


class Exercise(db.Model):
    __tablename__ = 'Exercise'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)
    duration = Column(String, nullable=False)
    exercise_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey('User.id'))
    user = relationship("User", back_populates="exercises")

    def __init__(self, description, duration, exercise_date):
        self.description = description
        self.duration = duration
        self.exercise_date = exercise_date

    def format(self):
        return {
          '_id': self.id,
          'description': self.description,
          'duration': self.duration,
          'date': self.exercise_date,
          'user': self.user
        }
    
    def short(self):
        return {
            'description': self.description,
            'duration': self.duration,
            'date': self.exercise_date,
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        # myparent.children.remove(somechild)
        db.session.delete(self)
        db.session.commit()


User.exercises = relationship("Exercise", order_by=Exercise.id, back_populates="user")
