from examples.GameServer.game_modules.game_dataaccess.dbtable.DataGameUser import DataGameUser
from pkg.ymd_dataaccess import YmdDataAccessBase


class RedisModule:
    def __init__(self, dataAccess: YmdDataAccessBase):
        self.dataAccess = dataAccess
    #获取数据
    def GetDataGameUser(self, userId:int)->DataGameUser:
        key:str ="GameUser:"+userId
        self.dataAccess.get_redis()
        return None


