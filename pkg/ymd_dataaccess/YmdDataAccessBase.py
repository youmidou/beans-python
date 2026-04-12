from dataclasses import dataclass
from typing import Optional

from pkg.ymd_dataaccess.ymd_mysql.mysql_client import MysqlClient, MysqlInfo
from pkg.ymd_dataaccess.ymd_redis.redis_client import RedisClient, RedisInfo


@dataclass
class DataAccessInfo:
    mysql_info: MysqlInfo = None
    redis_info: RedisInfo = None
    def __init__(self, mysql_info: MysqlInfo = None, redis_info: RedisInfo = None) -> None:
        self.mysql_info = mysql_info
        self.redis_info = redis_info



class YmdDataAccessBase:
    _mysql: MysqlClient = None
    _redis: RedisClient = None
    def __init__(self, info: DataAccessInfo):
        self._info = info
        self._mysql: MysqlClient = None
        self._redis: RedisClient = None

    def init(self) -> None:
        if self._info.mysql_info is not None:
            self._mysql = MysqlClient(self._info.mysql_info)
            self._mysql.connect()

        if self._info.redis_info is not None:
            self._redis = RedisClient(self._info.redis_info)
            self._redis.connect()

    def get_mysql(self) -> Optional[MysqlClient]:
        return self._mysql

    def get_redis(self) -> Optional[RedisClient]:
        return self._redis

    def close(self) -> None:
        if self._mysql:
            self._mysql.close()
            self._mysql = None
        if self._redis:
            self._redis.close()
            self._redis = None
