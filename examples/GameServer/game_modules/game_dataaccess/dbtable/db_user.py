#用户信息表
from sqlalchemy import Column, Integer


class DBUser:
    __tablename__ = "db_user"
    UserId = Column(Integer, primary_key=True)