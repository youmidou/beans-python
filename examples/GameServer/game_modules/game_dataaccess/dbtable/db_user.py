#用户信息表
from sqlalchemy import Column, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DBUser(Base):
    __tablename__ = "db_user"
    UserId = Column(Integer, primary_key=True)