from abc import ABC, abstractmethod

class Module(ABC):
    @abstractmethod
    def Init(self):
        pass

    @abstractmethod
    def AfterInit(self):
        pass

    @abstractmethod
    def BeforeShutdown(self):
        pass

    @abstractmethod
    def Shutdown(self):
        pass