from __future__ import annotations
from datetime import datetime
from database import Model


class VerifyModel(Model):
    def __init__(self) -> None:
        self.set(None, '', 0, datetime.now().timestamp())
        super().__init__()

    def set(self, id, code_verification:str, user_id:int, date_created:float = datetime.now().timestamp()) -> VerifyModel:
        self.id = id
        self.code_verification = str(code_verification)
        self.user_id = int(user_id)
        self.date_created = float(date_created)
        return self

    def parse(data) -> VerifyModel:
        # 0 -> id
        # 1 -> code_verification
        # 2 -> user_id
        # 3 -> date_created
        verifyModel = VerifyModel().set(data[0], data[1], data[2], data[3])
        return verifyModel

    def fromDict(data: dict) -> VerifyModel:
        verifyModel = VerifyModel()
        verifyModel.__dict__ = data
        return verifyModel
