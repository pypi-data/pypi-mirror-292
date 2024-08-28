from abc import ABC, abstractmethod


class ActionRobot(ABC):
    """
    This class is an abstract class that defines the methods that a robot should implement.
    """

    @abstractmethod
    def move_joints(self, j1, j2, j3, j4, j5, j6): ...

    @abstractmethod
    def get_joints(self): ...

    @abstractmethod
    def move_cartesian(self, x, y, z, roll, pitch, yaw): ...

    @abstractmethod
    def get_cartesian(self): ...

    @abstractmethod
    def move_to_home(self): ...

    @abstractmethod
    def move_to_zero(self): ...

    @abstractmethod
    def open_gripper(self, execution_time=1): ...

    @abstractmethod
    def close_gripper(self, execution_time=1): ...

    @abstractmethod
    def gripper_close_percentage(self, finger_value=1, actuation_time=1): ...

    @abstractmethod
    def set_velocity(self, velocity): ...

    @abstractmethod
    def calibrate(self): ...

    @abstractmethod
    def go_to_sleep(self): ...

    @abstractmethod
    def apply_emergency_stop(self): ...