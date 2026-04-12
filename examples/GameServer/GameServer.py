import asyncio

from examples.GameServer.game_modules.game_dataaccess.DataAccessManager import DataAccessManager
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
    builder:Builder = NewDefaultBuilder(True, svType, "pitaya.Cluster", "serverMetadata", cfg)
    app:App = builder.Build()
    app.RegisterModule(DataAccessManager(),"DataAccessManager")
    # 默认构建器
    #task6 = asyncio.create_task(handle_timeout())
    app.Start()
    await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
