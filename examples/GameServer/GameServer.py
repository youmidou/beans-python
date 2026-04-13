import asyncio
from enum import Enum

from examples.GameServer.game_modules.game_dataaccess.DataAccessManager import DataAccessManager
from examples.GameServer.game_modules.game_dataaccess.dbtable.DataGameUser import NewDataGameUser
from examples._def.svc_def import GameDef, GameModule
from pkg.app import App
from pkg.builder import NewDefaultBuilder, Builder
from pkg.config.config import PitayaConfig
from pkg.logger import logger

app: App

async def main():

    logger.SetLogger(logger.InitSystemLogger("./logs/game_server.log", logger.DEBUG))
    svType:str ="Game"
    cfg:PitayaConfig = PitayaConfig()
    logger.Log.Info("🚀 开始服务器启动完成")
    builder:Builder = NewDefaultBuilder(True, svType, "pitaya.Cluster", cfg)
    app:App = builder.Build()

    dataAccess = DataAccessManager()
    dataAccess.initialize()

    dataGameUser = dataAccess.GetDataGameUser(1)
    if dataGameUser is None:
        data = NewDataGameUser(1)
        dataAccess.SetDataGameUser(data.UserId, data)

    logger.Log.Info("----------------")

    #app.RegisterModule(DataAccessManager(),"DataAccessManager")
    # 默认构建器
    #task6 = asyncio.create_task(handle_timeout())
    app.Start()
    #uv add redis --upgrade
    await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
