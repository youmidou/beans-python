from dataclasses import dataclass


@dataclass
class PostgresqlInfo:
    host: str
    port: int
    user: str
    password: str
    database: str

#链接Postgresql客户端
class PostgresqlClient:
    def __init__(self,info:PostgresqlInfo):
        pass

    def connect(self):
        pass

    def close(self):
        pass