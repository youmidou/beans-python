#默认构建器
from pkg.app import App
from pkg.config.config import PitayaConfig


class Builder:
    def __init__(self):
        self.app = None

    def Build(self)->App:
        self.app = App()
        return self.app


def NewDefaultBuilder(isFrontend:bool,serverType:str,serverMode:str,pitayaConfig:PitayaConfig)->Builder:
    builder = Builder()
    return builder
