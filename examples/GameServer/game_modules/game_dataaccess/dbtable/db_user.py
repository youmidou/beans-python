#用户信息表
from sqlalchemy import Column, Integer
from pkg.ymd_dataaccess.ymd_postgresql.postgresql_client import Base


class DBUser(Base):
    __tablename__ = "db_user"
    UserId = Column(Integer, primary_key=True)