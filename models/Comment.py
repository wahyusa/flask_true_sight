from __future__ import annotations
from datetime import datetime
from database import Model


class Comment(Model):
    def __init__(self) -> None:
        self.set(None, -1, -1, '', datetime.now().timestamp())
        super().__init__()

    def set(self, id, author_id:int, post_id:int, comment_text:str, date_created:int = datetime.now().timestamp()) -> Comment:
        self.id = id
        self.post_id = int(post_id)
        self.author_id = int(author_id)
        self.comment_text = str(comment_text)
        self.date_created = float(date_created)
        return self

    def parse(data) -> Comment:
        # 0 -> id
        # 1 -> post_id
        # 2 -> author_id
        # 3 -> comment_text
        # 4 -> date_created
        comment = Comment().set(data[0], data[2], data[1], data[3], data[4])
        return comment

    def fromDict(data: dict) -> Comment:
        comment = Comment()
        comment.__dict__ = data
        return comment
