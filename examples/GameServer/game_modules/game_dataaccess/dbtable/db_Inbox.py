#收件箱表
from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DBInbox(Base):
    __tablename__ = "db_inbox"
    UserId = Column(Integer, primary_key=True)
