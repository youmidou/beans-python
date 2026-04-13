#收件箱表
from sqlalchemy import Column, Integer


class DBInbox:
    __tablename__ = "db_inbox"
    UserId = Column(Integer, primary_key=True)
