#角色信息表
from sqlalchemy import Column, Integer, String
from pkg.ymd_dataaccess.ymd_postgresql.postgresql_client import Base


class DBRole(Base):
    __tablename__ = "db_role"
    UserId = Column(Integer, primary_key=True)
    NickName = Column(String) #昵称
