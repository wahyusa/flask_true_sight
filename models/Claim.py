from __future__ import annotations
from database import Model


class Claim(Model):
    def __init__(self) -> None:
        self.set(None, '', '', False, 0, '', 0, '')
        super().__init__()

    def set(self, id: int, title: str, description: str, fake: bool, author_id: int, author_username:str, date_created: int, attachment: str, url: str = None, upvote: int = 0, downvote: int = 0, num_click: int = 0, verified_by: int = None, comment_id: int = None) -> Claim:
        self.id = id
        self.title = title
        self.description = description
        self.author_username = author_username
        self.fake = fake
        self.author_id = author_id
        self.date_created = date_created
        self.attachment = attachment
        self.url = url
        self.upvote = upvote
        self.downvote = downvote
        self.num_click = num_click
        self.verified_by = verified_by
        self.comment_id = comment_id
        return self

    def get(self):
        data = self.__dict__
        data['fake'] = 1 if data['fake'] else 0
        return data

    def parse(data) -> Claim:
        # 0 -> id
        # 1 -> title
        # 2 -> description
        # 3 -> fake
        # 4 -> author_id
        # 5 -> author_username
        # 6 -> date_created
        # 7 -> attachment
        # 8 -> url
        # 9 -> upvote
        # 10 -> downvote
        # 11 -> num_click
        # 12 -> verified_by
        # 13 -> comment_id

        claim = Claim().set(data[0], data[1], data[2], int(data[3]) == 1, data[4], data[5], data[6],
                            data[7], data[8], data[9], data[10], data[11], data[12], data[13])
        return claim

    def fromDict(data: dict) -> Claim:
        claim = Claim()
        claim.__dict__ = data
        return claim
