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

    # 基础 String 操作
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """设置键值，支持过期时间（秒）"""
        return self.get_client().set(key, value, ex=ex)

    def get(self, key: str) -> Optional[bytes]:
        """获取键值"""
        return self.get_client().get(key)

    def delete(self, *keys: str) -> int:
        """删除一个或多个键"""
        return self.get_client().delete(*keys)

    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        return self.get_client().exists(key) > 0

    def expire(self, key: str, seconds: int) -> bool:
        """设置键的过期时间"""
        return self.get_client().expire(key, seconds)

    def ttl(self, key: str) -> int:
        """获取键的剩余过期时间"""
        return self.get_client().ttl(key)

    # Hash 操作
    def hset(self, name: str, key: str, value: Any) -> int:
        """设置 hash 字段"""
        return self.get_client().hset(name, key, value)

    def hget(self, name: str, key: str) -> Optional[bytes]:
        """获取 hash 字段"""
        return self.get_client().hget(name, key)

    def hgetall(self, name: str) -> dict:
        """获取 hash 所有字段"""
        return self.get_client().hgetall(name)

    def hdel(self, name: str, *keys: str) -> int:
        """删除 hash 字段"""
        return self.get_client().hdel(name, *keys)

    def hexists(self, name: str, key: str) -> bool:
        """检查 hash 字段是否存在"""
        return self.get_client().hexists(name, key)

    def hkeys(self, name: str) -> list:
        """获取 hash 所有字段名"""
        return self.get_client().hkeys(name)

    def hvals(self, name: str) -> list:
        """获取 hash 所有值"""
        return self.get_client().hvals(name)

    def hlen(self, name: str) -> int:
        """获取 hash 字段数量"""
        return self.get_client().hlen(name)

    # List 操作
    def lpush(self, name: str, *values: Any) -> int:
        """从左侧推入列表"""
        return self.get_client().lpush(name, *values)

    def rpush(self, name: str, *values: Any) -> int:
        """从右侧推入列表"""
        return self.get_client().rpush(name, *values)

    def lpop(self, name: str) -> Optional[bytes]:
        """从左侧弹出列表元素"""
        return self.get_client().lpop(name)

    def rpop(self, name: str) -> Optional[bytes]:
        """从右侧弹出列表元素"""
        return self.get_client().rpop(name)

    def lrange(self, name: str, start: int, end: int) -> list:
        """获取列表范围元素"""
        return self.get_client().lrange(name, start, end)

    def llen(self, name: str) -> int:
        """获取列表长度"""
        return self.get_client().llen(name)

    # Set 操作
    def sadd(self, name: str, *values: Any) -> int:
        """添加集合成员"""
        return self.get_client().sadd(name, *values)

    def srem(self, name: str, *values: Any) -> int:
        """移除集合成员"""
        return self.get_client().srem(name, *values)

    def smembers(self, name: str) -> set:
        """获取集合所有成员"""
        return self.get_client().smembers(name)

    def sismember(self, name: str, value: Any) -> bool:
        """检查是否是集合成员"""
        return self.get_client().sismember(name, value)

    def scard(self, name: str) -> int:
        """获取集合成员数量"""
        return self.get_client().scard(name)

    # Sorted Set 操作
    def zadd(self, name: str, mapping: dict) -> int:
        """添加有序集合成员"""
        return self.get_client().zadd(name, mapping)

    def zrem(self, name: str, *values: Any) -> int:
        """移除有序集合成员"""
        return self.get_client().zrem(name, *values)

    def zrange(self, name: str, start: int, end: int, withscores: bool = False) -> list:
        """获取有序集合范围成员（按分数从小到大）"""
        return self.get_client().zrange(name, start, end, withscores=withscores)

    def zrevrange(self, name: str, start: int, end: int, withscores: bool = False) -> list:
        """获取有序集合范围成员（按分数从大到小）"""
        return self.get_client().zrevrange(name, start, end, withscores=withscores)

    def zscore(self, name: str, value: Any) -> Optional[float]:
        """获取有序集合成员分数"""
        return self.get_client().zscore(name, value)

    def zcard(self, name: str) -> int:
        """获取有序集合成员数量"""
        return self.get_client().zcard(name)

    # 其他操作
    def incr(self, key: str, amount: int = 1) -> int:
        """递增"""
        return self.get_client().incr(key, amount)

    def decr(self, key: str, amount: int = 1) -> int:
        """递减"""
        return self.get_client().decr(key, amount)

    def ping(self) -> bool:
        """测试连接"""
        return self.get_client().ping()
