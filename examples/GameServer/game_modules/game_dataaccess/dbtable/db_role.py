#角色信息表
from sqlalchemy import Column, Integer


class DBRole(object):
    __tablename__ = "db_role"
    UserId = Column(Integer, primary_key=True)
