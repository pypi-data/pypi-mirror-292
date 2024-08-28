from rria_api.gen3.api_gen3.gen3_api import Gen3Api
from rria_api.abstract_robot.action_robot import ActionRobot

from kortex_api.autogen.client_stubs.BaseClientRpc import BaseClient
from kortex_api.autogen.client_stubs.BaseCyclicClientRpc import BaseCyclicClient


class ActionGen3(ActionRobot):
    """
    This class is used to perform actions with the Gen3 robot.
    This class is inherited from the ActionRobot class.
    """
    def __init__(self, route):
        """
        This method is used to initialize the Gen3 robot object.

        Args:
            route: the route of the robot, gets from the connection object
        """
        self.route = route
        self.base = BaseClient(self.route)
        self.base_cyclic = BaseCyclicClient(self.route)

    def move_joints(self, j1, j2, j3, j4, j5, j6):
        """
        This method is used to movement the robot joints.

        Args:
            j1 (float): The desired position for the first joint
            j2 (float): The desired position for the second joint
            j3 (float): The desired position for the third joint
            j4 (float): The desired position for the fourth joint
            j5 (float): The desired position for the fifth joint
            j6 (float): The desired position for the sixth joint
        """
        Gen3Api().angular_movement(self.base, [j1, j2, j3, j4, j5, j6])

    def get_joints(self):
        """
        This method is used to reading the robot joints.

        Returns:
            list: an angles list of the robot joints in degrees
        """
        return Gen3Api().get_joints(self.base_cyclic)

    def move_cartesian(self, x, y, z, roll, pitch, yaw):
        """
        This method is used to movement of the robot in cartesian space.

        Args:
            x (float): The x coordinate of the robot in meters
            y (float): The y coordinate of the robot in meters
            z (float): The z coordinate of the robot in meters
            roll (float): The roll angle of the robot in degrees
            pitch (float): The pitch angle of the robot in degrees
            yaw (float): The yaw angle of the robot in degrees
        """
        Gen3Api().cartesian_movement(self.base, [x, y, z, roll, pitch, yaw])

    def get_cartesian(self):
        """
        This method is used to reading the robot cartesian coordinates.

        Returns:
            list: a cartesian list coordinates of the robot in meters and degrees
        """
        return Gen3Api().get_cartesian(self.base_cyclic)

    def move_to_home(self):
        """
        This method is used to movement the robot to its home position.
        """
        Gen3Api().move_to_home(self.base)

    def move_to_zero(self):
        """
        This method is used to movement the robot to its zero position.
        """
        joints_list = [0, 0, 0, 0, 0, 0]
        Gen3Api().angular_movement(self.base, joints_list)

    def open_gripper(self, execution_time=1):
        """
        This method is used to opening the robot gripper.

        Args:
            execution_time: execution time in seconds
        """
        Gen3Api().open_gripper(self.base, execution_time)

    def close_gripper(self, execution_time=1):
        """
        This method is used to closing the robot gripper.

        Args:
            execution_time: execution time in seconds
        """
        Gen3Api().close_gripper(self.base, execution_time)

    def gripper_close_percentage(self, finger_value=1, actuation_time=1):
        """
        This method is used to closing the robot gripper to a specific percentage

        Args:
            finger_value: finger value in percentage
            actuation_time: finger actuation time in seconds
        """
        Gen3Api().gripper_close_percentage(self.base, finger_value, actuation_time)

    def set_velocity(self, velocity):
        """
        This method is used to setting the robot velocity

        Args:
            velocity: the velocity value in m/s
        """
        Gen3Api().set_velocity(self.base, velocity)

    def calibrate(self):
        """
        This method is used to calibration the robot.
        """
        raise NotImplementedError("Calibrate method is not implemented for Gen3 robot")

    def go_to_sleep(self):
        """
        This method is used to robot going to sleep.
        """
        joints_list = [0.0, 26, 149.9, 0.0, 0.0, 0.0]
        Gen3Api().angular_movement(self.base, joints_list)

    def apply_emergency_stop(self):
        """
        This method is used to application an emergency stop to the robot.
        """
        Gen3Api().apply_emergency_stop(self.base)
