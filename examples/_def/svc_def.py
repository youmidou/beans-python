from enum import Enum

class GameDef:
    DataAccessManager = "DataAccessManager"  # 数据访问模块

#游戏模块枚举GameModule
class GameModule(Enum):
    DataAccessManager = "DataAccessManager"    # 数据访问模块

#
class GameSvc(Enum):
    Login = "Login"    # 进入游戏
