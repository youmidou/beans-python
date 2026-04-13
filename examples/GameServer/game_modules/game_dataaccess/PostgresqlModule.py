from pkg.ymd_dataaccess import YmdDataAccessBase


class PostgresqlModule:
    def __init__(self, dataAccess: YmdDataAccessBase):
        self.dataAccess = dataAccess
        self._pg = dataAccess.get_postgresql()

    def GetDataGameUser(self,userId:int):
        self.dataAccess.get_postgresql()