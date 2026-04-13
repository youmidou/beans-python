#角色信息表
from sqlalchemy import Column, Integer, String


class DBRole(object):
    __tablename__ = "db_role"
    UserId = Column(Integer, primary_key=True)
    NickName = Column(String) #昵称
