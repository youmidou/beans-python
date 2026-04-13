from pkg.ymd_dataaccess import YmdDataAccessBase


class PostgresqlModule:
    def __init__(self, dataAccess: YmdDataAccessBase):
        self.dataAccess = dataAccess
