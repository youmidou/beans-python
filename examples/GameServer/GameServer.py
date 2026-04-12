import asyncio

from pkg.logger import logger

async def main():

    logger.SetLogger(logger.InitSystemLogger("./logs/game_server.log", logger.DEBUG))

    logger.Log.Info("🚀 服务器启动完成")

    #task6 = asyncio.create_task(handle_timeout())
    await asyncio.sleep(3)

if __name__ == "__main__":
    asyncio.run(main())
