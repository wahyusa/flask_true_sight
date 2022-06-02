from __future__ import annotations
from datetime import datetime
from database import Model


class ApiSession(Model):
    def __init__(self) -> None:
        self.set(None, None, None, datetime.now().timestamp(), None)
        super().__init__()

    def set(self, id:int, api_key: str, user_id:int, date_created:int, expired:int) -> ApiSession:
        self.id = id
        self.api_key = api_key
        self.user_id = user_id
        self.date_created = date_created
        self.expired = expired
        return self

    def parse(data) -> ApiSession:
        # 0 -> id
        # 1 -> api_key
        # 2 -> user_id
        # 3 -> date_created
        # 4 -> expired
        apiSession = ApiSession().set(data[0], data[1], data[2], data[3], data[4])
        return apiSession

    def fromDict(data: dict) -> ApiSession:
        apiSession = ApiSession()
        apiSession.__dict__ = data
        return apiSession
