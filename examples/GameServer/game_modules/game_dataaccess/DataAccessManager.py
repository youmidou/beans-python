import logging
from typing import Optional

from examples.GameServer.game_modules.game_dataaccess.PostgresqlModule import PostgresqlModule

from examples.GameServer.game_modules.game_dataaccess.dbtable.DataGameUser import DataGameUser
from examples.GameServer.game_modules.game_dataaccess.dbtable.db_Inbox import DBInbox
from examples.GameServer.game_modules.game_dataaccess.dbtable.db_role import DBRole
from examples.GameServer.game_modules.game_dataaccess.dbtable.db_user import DBUser
from pkg.logger import logger
from pkg.ymd_dataaccess.YmdDataAccessBase import YmdDataAccessBase, DataAccessInfo
from examples.GameServer.game_modules.game_dataaccess.MysqlModule import MysqlModule
from examples.GameServer.game_modules.game_dataaccess.RedisModule import RedisModule

from pkg.ymd_dataaccess.ymd_postgresql.postgresql_client import PostgresqlInfo
from pkg.ymd_dataaccess.ymd_mysql.mysql_client import MysqlInfo
from pkg.ymd_dataaccess.ymd_redis.redis_client import RedisInfo


class DataAccessManager:
    _instance:DataAccessManager | None = None

    redisModule: RedisModule = None
    postgresqlModule: PostgresqlModule = None
    mysqlModule: MysqlModule = None
    dataAccess: YmdDataAccessBase = None

    def __new__(cls) -> DataAccessManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self._initialized = True

    def initialize(self) -> None:
        """Initialize all data access modules"""
        logger.Log.Info("🚀 初始化数据库...")
        info = DataAccessInfo()
        info.redis_info = RedisInfo(
                host="127.0.0.1",
                port=10000,
                db=0,
            )
        # 如果需要 PostgreSQL，取消注释以下代码
        info.postgresql_info = PostgresqlInfo(
             host="127.0.0.1",
             port=10001,
             user="postgres",
             password="12345678",
             database="gamedb",
         )

        # info.mysql_info = MysqlInfo(
        #         host="127.0.0.1",
        #         port=3306,
        #         user="root",
        #         password="12345678",
        #         database="fever3",
        #         pool_size=30,
        #         max_overflow=50,
        #         pool_recycle=900,
        #     )

        try:
            # Initialize YmdDataAccessBase
            self.dataAccess = YmdDataAccessBase(info)

            # 先连接数据库（会自动创建数据库）
            self.dataAccess.Connect()
            logger.Log.Info("🚀 数据库链接成功...")

            # 注册表自动迁移 创建表结构
            self.dataAccess.AutoMigrate(DBUser,DBRole,DBInbox)
            logger.Log.Info("✅ 数据表结构创建/更新成功")

            # Initialize specific modules
            self.redisModule = RedisModule(self.dataAccess)
            if info.postgresql_info:
                self.postgresqlModule = PostgresqlModule(self.dataAccess)
            #self.mysqlModule = MysqlModule(self.dataAccess)
            logger.Log.Info("DataAccessManager initialized successfully")

        except Exception as e:
            logger.Log.Error(f"DataAccessManager initialization failed: {e}")
            raise

    def SetDataGameUser(self, userId: int, dataGameUser: DataGameUser, isPgsql: bool = False) -> bool:
        """保存玩家数据"""
        # 保存到 Redis
        _, err = self.redisModule.SetDataGameUser(userId, dataGameUser)
        if err is not None:
            logger.Log.Error(f"SetDataGameUser to Redis failed: {err}")
            return False

        # 如果需要，保存到 PostgreSQL
        if isPgsql and self.postgresqlModule is not None:
            _, err = self.postgresqlModule.SetDataGameUser(userId, dataGameUser)
            if err is not None:
                logger.Log.Error(f"SetDataGameUser to PostgreSQL failed: {err}")
                return False

        return True

    def GetDataGameUser(self, userId: int) -> DataGameUser:
        """获取玩家数据（优先从 Redis，缓存未命中则从 PostgreSQL 加载）"""
        # 先从 Redis 获取
        data, err = self.redisModule.GetDataGameUser(userId)
        if err is not None:
            logger.Log.Error(f"GetDataGameUser from Redis failed: {err}")

        # 如果 Redis 没有数据，从 PostgreSQL 加载
        if data is None and self.postgresqlModule is not None:
            data, err = self.postgresqlModule.GetDataGameUser(userId)
            if err is not None:
                #logger.Log.Error(f"GetDataGameUser from PostgreSQL failed: {err}")
                return None

        return data
