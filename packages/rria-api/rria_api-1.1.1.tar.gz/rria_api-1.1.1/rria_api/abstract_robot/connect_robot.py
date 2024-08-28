from abc import ABC, abstractmethod


class ConnectRobot(ABC):
    @abstractmethod
    def connect_robot(self): ...

    @abstractmethod
    def disconnect_robot(self): ...
