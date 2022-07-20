from __future__ import annotations
from datetime import datetime
from database import Model


class User(Model):
    def __init__(self) -> None:
        self.set(None, '', '', '', '', datetime.now().timestamp())
        super().__init__()

    def set(self, id, username: str, full_name: str, email: str, password: str, date_created: int, avatar:str = None, verified: int = 0, apioauth: str = None, votes: str = None, bookmarks: str = None, role: int = -1) -> User:
        self.id = id
        self.username = username
        self.full_name = full_name
        self.email = email
        self.password = password
        self.date_created = date_created
        self.avatar = avatar
        self.apioauth = apioauth
        self.verified = int(verified)
        self.votes = votes
        self.bookmarks = bookmarks
        self.role = role
        return self

    def parse(data) -> User:
        # 0 -> id
        # 1 -> username
        # 2 -> full_name
        # 3 -> email
        # 4 -> apioauth
        # 5 -> password
        # 6 -> date_created
        # 7 -> Avatar
        # 8 -> verified
        # 9 -> votes
        # 10 -> bookmarks
        # 11 -> role
        user = User().set(data[0], data[1], data[2], data[3], data[5], data[6], data[7],
                          int(data[8]) == 1, data[4], data[9], data[10], data[11])
        return user

    def fromDict(data: dict) -> User:
        user = User()
        user.__dict__ = data
        return user
