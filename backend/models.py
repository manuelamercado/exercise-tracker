import os
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

# database_name = "capstone"
# database_path = "postgresql://{}/{}".format(os.environ['DATABASE_URL'], database_name)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
  # app.config["SQLALCHEMY_DATABASE_URI"] = database_path
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

  id = Column(Integer, primary_key=True)
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
