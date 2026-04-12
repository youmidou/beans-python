import logging
from typing import Optional

from pkg.logger import logger
from pkg.ymd_dataaccess.YmdDataAccessBase import YmdDataAccessBase, DataAccessInfo
from examples.GameServer.game_modules.game_dataaccess.MysqlModule import MysqlModule
from examples.GameServer.game_modules.game_dataaccess.RedisModule import RedisModule
from pkg.ymd_dataaccess.ymd_mysql.mysql_client import MysqlInfo
from pkg.ymd_dataaccess.ymd_redis.redis_client import RedisInfo


class DataAccessManager:
    _instance:DataAccessManager | None = None

    def __new__(cls) -> DataAccessManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        self.logger = logging.getLogger(__name__)
        self.dataAccess: Optional[YmdDataAccessBase] = None
        self.mysqlModule: Optional[MysqlModule] = None
        self.redisModule: Optional[RedisModule] = None
        self.is_initialized = False

    def initialize(self) -> None:
        """Initialize all data access modules"""
        info = DataAccessInfo()
        info.mysql_info = MysqlInfo(
                host="127.0.0.1",
                port=3306,
                user="root",
                password="12345678",
                database="fever2",
                pool_size=30,
                max_overflow=50,
                pool_recycle=900,
            )
        info.redis_info = RedisInfo(
                host="127.0.0.1",
                port=6379,
                db=0,
            )

        try:
            # Initialize YmdDataAccessBase
            self.dataAccess = YmdDataAccessBase(info)
            self.dataAccess.init()

            # Initialize specific modules
            self.mysqlModule = MysqlModule(self.dataAccess)
            self.redisModule = RedisModule(self.dataAccess)
            self.is_initialized = True
            logger.Log.Info("DataAccessManager initialized successfully")

        except Exception as e:
            logger.Log.Error(f"DataAccessManager initialization failed: {e}")
            raise
    #获取玩家
    def GetDataGameUser(self,userId:int):

        pass