from __future__ import annotations
from database import Model


class User(Model):
    def __init__(self) -> None:
        self.set(None, '', '', '', '')
        super().__init__()

    def set(self, id, username: str, email: str, password: str, date_created: int, verified: bool = False, apioauth: str = None, votes: str = None, bookmarks: str = None) -> User:
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.date_created = date_created
        self.apioauth = apioauth
        self.verified = verified
        self.votes = votes
        self.bookmarks = bookmarks
        return self

    def parse(data) -> User:
        user = User().set(data[0], data[1], data[2], data[4], data[5], data[3],
                          data[6], data[7], data[8])
        return user

    def fromDict(data: dict) -> User:
        user = User()
        user.__dict__ = data
        return user
