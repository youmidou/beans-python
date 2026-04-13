#角色信息表
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DBRole(Base):
    __tablename__ = "db_role"
    UserId = Column(Integer, primary_key=True)
    NickName = Column(String) #昵称
