import os
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (
  Column, String, Integer, DateTime, ForeignKey, create_engine
)
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

    def __init__(self, username):
        self.username = username

    def format(self):
        return {
          'id': self.id,
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
