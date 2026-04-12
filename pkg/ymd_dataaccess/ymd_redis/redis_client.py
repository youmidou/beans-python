import redis
from typing import Optional, Any
from dataclasses import dataclass, field


@dataclass
class RedisInfo:
    host: str = "127.0.0.1"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    pool_size: int = 10
    min_idle_conns: int = 5
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    decode_responses: bool = False


class RedisClient:
    def __init__(self, info: RedisInfo):
        self._info = info
        self._client: Optional[redis.StrictRedis] = None

    def connect(self) -> None:
        pool = redis.ConnectionPool(
            host=self._info.host,
            port=self._info.port,
            db=self._info.db,
            password=self._info.password or None,
            max_connections=self._info.pool_size,
            socket_timeout=self._info.socket_timeout,
            socket_connect_timeout=self._info.socket_connect_timeout,
            decode_responses=self._info.decode_responses,
        )
        self._client = redis.StrictRedis(connection_pool=pool)
        self._client.ping()

    def get_client(self) -> redis.StrictRedis:
        if self._client is None:
            raise RuntimeError("RedisClient not connected. Call connect() first.")
        return self._client

    def AutoMigrate(self, *models_or_bases: Any) -> None:
        pass

    def close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None