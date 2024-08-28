from enum import Enum, auto
import typing as t


class RobotEnum(Enum):
    """
    Enum for robot types. Choose the robot type you want to use.

    Attributes:
        GEN3_LITE: The kinova Gen3 lite robot.
        NED: The Niryo Ned robot.
        DUMMY: A dummy robot for testing purposes.
    """
    GEN3_LITE = auto()
    NED = auto()
    DUMMY = auto()
