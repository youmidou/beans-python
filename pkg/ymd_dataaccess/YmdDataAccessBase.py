from dataclasses import dataclass
from typing import Optional

from pkg.logger import logger
from pkg.ymd_dataaccess.ymd_mysql.mysql_client import MysqlClient, MysqlInfo
from pkg.ymd_dataaccess.ymd_postgresql.postgresql_client import PostgresqlInfo, PostgresqlClient
from pkg.ymd_dataaccess.ymd_redis.redis_client import RedisClient, RedisInfo


@dataclass
class DataAccessInfo:
    postgresql_info: PostgresqlInfo = None
    mysql_info: MysqlInfo = None
    redis_info: RedisInfo = None


class YmdDataAccessBase:
    _postgresql: PostgresqlClient = None
    _mysql: MysqlClient = None
    _redis: RedisClient = None
    def __init__(self, info: DataAccessInfo):
        self._info = info

    def init(self) -> None:
        logger.Log.info("YmdDataAccessBase.__init__")
        if self._info.postgresql_info is not None:
            self._postgresql = PostgresqlClient(self._info.postgresql_info)
            self._postgresql.connect()

        if self._info.mysql_info is not None:
            self._mysql = MysqlClient(self._info.mysql_info)
            self._mysql.connect()

        if self._info.redis_info is not None:
            self._redis = RedisClient(self._info.redis_info)
            self._redis.connect()

    def get_postgresql(self) -> Optional[PostgresqlClient]:
        return self._postgresql

    def get_mysql(self) -> Optional[MysqlClient]:
        return self._mysql

    def get_redis(self) -> Optional[RedisClient]:
        return self._redis

    def close(self) -> None:
        if self._postgresql:
            self._postgresql.close()
            self._postgresql = None

        if self._mysql:
            self._mysql.close()
            self._mysql = None
        if self._redis:
            self._redis.close()
            self._redis = None
