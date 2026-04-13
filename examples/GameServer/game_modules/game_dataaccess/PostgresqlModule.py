from typing import Tuple, Optional
from pkg.ymd_dataaccess import YmdDataAccessBase
from examples.GameServer.game_modules.game_dataaccess.dbtable.DataGameUser import DataGameUser
from examples.GameServer.game_modules.game_dataaccess.dbtable.db_role import DBRole
from examples.GameServer.game_modules.game_dataaccess.dbtable.db_Inbox import DBInbox
from pkg.logger import logger


class PostgresqlModule:
    def __init__(self, dataAccess: YmdDataAccessBase):
        self.dataAccess = dataAccess
        self._pg = dataAccess.get_postgresql()

    def GetDataGameUser(self, userId: int) -> Tuple[Optional[DataGameUser], Optional[Exception]]:
        """从 PostgreSQL 获取玩家数据"""
        try:
            session = self._pg.get_session()

            # 查询 DBRole
            role = session.query(DBRole).filter(DBRole.UserId == userId).first()
            if role is None:
                session.close()
                return None, None

            # 查询 DBInbox
            inbox = session.query(DBInbox).filter(DBInbox.UserId == userId).first()

            session.close()

            # 构建 DataGameUser
            gameUser = DataGameUser(userId)
            gameUser.DBRole = role
            gameUser.DBInbox = inbox if inbox else DBInbox()

            return gameUser, None

        except Exception as e:
            logger.Log.Error(f"GetDataGameUser from PostgreSQL failed: {e}")
            return None, e

    def SetDataGameUser(self, userId: int, dataGameUser: DataGameUser) -> Tuple[bool, Optional[Exception]]:
        """保存玩家数据到 PostgreSQL"""
        try:
            session = self._pg.get_session()

            # 保存或更新 DBRole
            existing_role = session.query(DBRole).filter(DBRole.UserId == userId).first()
            if existing_role:
                existing_role.NickName = dataGameUser.DBRole.NickName
            else:
                session.add(dataGameUser.DBRole)

            # 保存或更新 DBInbox
            existing_inbox = session.query(DBInbox).filter(DBInbox.UserId == userId).first()
            if existing_inbox is None and dataGameUser.DBInbox:
                session.add(dataGameUser.DBInbox)

            session.commit()
            session.close()

            return True, None

        except Exception as e:
            logger.Log.Error(f"SetDataGameUser to PostgreSQL failed: {e}")
            if session:
                session.rollback()
                session.close()
            return False, e