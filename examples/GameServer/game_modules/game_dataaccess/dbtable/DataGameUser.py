from examples.GameServer.game_modules.game_dataaccess.dbtable.db_Inbox import DBInbox
from examples.GameServer.game_modules.game_dataaccess.dbtable.db_role import DBRole


class DataGameUser:

    def __init__(self,userId:int):
        self.UserId = userId
        self.DBRole:DBRole
        self.DBInbox:DBInbox


def NewDataGameUser(userId:int):
    t:DataGameUser = DataGameUser(userId)
    t.DBRole = DBRole()
    t.DBRole.UserId = userId
    t.DBRole.NickName ="user:" + str(userId)

    #收件信息
    t.DBInbox = DBInbox()
    t.DBInbox.UserId = userId

    return t