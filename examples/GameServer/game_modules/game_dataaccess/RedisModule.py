from pkg.ymd_dataaccess import YmdDataAccessBase


class RedisModule:
    def __init__(self, dataAccess: YmdDataAccessBase):
        self.dataAccess = dataAccess
        self._redis = dataAccess.get_redis()


