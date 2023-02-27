from sqlalchemy import Column, String
from database import Base


class User(Base):
    __tablename__ = 'user'

    username = Column(String, primary_key=True)
    password = Column(String)
    
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return "username:{}".format(self.username)