import json
from typing import Tuple, Optional
from examples.GameServer.game_modules.game_dataaccess.dbtable.DataGameUser import DataGameUser
from examples.GameServer.game_modules.game_dataaccess.dbtable.db_role import DBRole
from examples.GameServer.game_modules.game_dataaccess.dbtable.db_Inbox import DBInbox
from pkg.ymd_dataaccess import YmdDataAccessBase
from pkg.logger import logger


class RedisModule:
    def __init__(self, dataAccess: YmdDataAccessBase):
        self.dataAccess = dataAccess
        self._redis = dataAccess.get_redis()

    def SetDataGameUser(self, userId: int, dataGameUser: DataGameUser) -> Tuple[bool, Optional[Exception]]:
        """保存玩家数据到 Redis"""
        try:
            key = f"GameUser:{userId}"

            # 将 DataGameUser 转换为字典
            data = {
                "UserId": dataGameUser.UserId,
                "role": {
                    "UserId": dataGameUser.DBRole.UserId,
                    "NickName": dataGameUser.DBRole.NickName
                },
                "inbox": {
                    "UserId": dataGameUser.DBInbox.UserId
                }
            }

            # 序列化为 JSON 并保存
            value = json.dumps(data)
            self._redis.set(key, value, ex=3600)  # 1小时过期
            return True, None

        except Exception as e:
            logger.Log.Error(f"SetDataGameUser to Redis failed: {e}")
            return False, e

    def GetDataGameUser(self, userId: int) -> Tuple[Optional[DataGameUser], Optional[Exception]]:
        """从 Redis 获取玩家数据"""
        try:
            key = f"GameUser:{userId}"
            value = self._redis.get(key)

            if value is None:
                return None, None

            # 反序列化 JSON
            data = json.loads(value.decode('utf-8'))

            # 重建 DataGameUser 对象
            gameUser = DataGameUser(data["UserId"])

            # 重建 DBRole
            gameUser.DBRole = DBRole()
            gameUser.DBRole.UserId = data["role"]["UserId"]
            gameUser.DBRole.NickName = data["role"]["NickName"]

            # 重建 DBInbox
            gameUser.DBInbox = DBInbox()
            gameUser.DBInbox.UserId = data["inbox"]["UserId"]

            return gameUser, None

        except Exception as e:
            logger.Log.Error(f"GetDataGameUser from Redis failed: {e}")
            return None, e





