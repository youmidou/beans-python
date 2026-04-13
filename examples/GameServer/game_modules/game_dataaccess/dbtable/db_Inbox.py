#收件箱表
from sqlalchemy import Column, Integer
from pkg.ymd_dataaccess.ymd_postgresql.postgresql_client import Base


class DBInbox(Base):
    __tablename__ = "db_inbox"
    UserId = Column(Integer, primary_key=True)
