from sqlalchemy import Column, String, DateTime, Integer
from database import Base
from datetime import datetime


class Bulletin(Base):
    __tablename__ = 'bulletin'

    postId = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    title = Column(String)
    content = Column(String)
    postDate = Column(DateTime)

    def __init__(self, username, title, content):
        self.title = title
        self.username = username
        self.title = title
        self.content = content
        self.postDate = datetime.now()

    def to_json(self):
        return {
            "postId": self.postId,
            "username": self.username,
            "title": self.title,
            "content": self.content,
            "postDate": self.postDate.isoformat()
        }

    def __repr__(self):
        return "username: {}, content: {}, postDate:{} ".format(self.username, self.content, self.postDate)
