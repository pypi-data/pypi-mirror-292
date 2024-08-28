import math

from rria_api.abstract_robot.action_robot import ActionRobot


class ActionNed(ActionRobot):
    """
    This class is used to perform actions with the NED robot.
    This class is inherited from the ActionRobot class.
    """
    def __init__(self, robot_object):
        """
        This method is used to initialize the NED robot object.

        Args:
            robot_object: the robot object, gets from the connection object
        """
        self.robot_object = robot_object

    def move_joints(self, j1, j2, j3, j4, j5, j6):
        """
        This method is used to movement the robot joints.
        These values are in degrees, so we need to convert them to radians because the robot works with radians.

        Args:
            j1 (float): The desired position for the first joint
            j2 (float): The desired position for the second joint
            j3 (float): The desired position for the third joint
            j4 (float): The desired position for the fourth joint
            j5 (float): The desired position for the fifth joint
            j6 (float): The desired position for the sixth joint
        """
        trans = math.pi / 180
        self.robot_object.move_joints(j1 * trans, j2 * trans, j3 * trans, j4 * trans, j5 * trans, j6 * trans)

    def get_joints(self):
        """
        This method is used to reading the robot joints.
        These values are in radians, so we need to convert them to degrees because the robot works with degrees.

        Returns:
            list: an angles list of the robot joints in degrees
        """
        joints_rad = self.robot_object.get_joints()
        joints_degrees = [round(joint * 180 / math.pi, 3) for joint in joints_rad]
        return joints_degrees

    def move_cartesian(self, x, y, z, roll, pitch, yaw):
        """
        This method is used to movement of the robot in cartesian space.
        These values are in degrees, so we need to convert them to radians because the robot works with radians.

        Args:
            x (float): The x coordinate of the robot in meters
            y (float): The y coordinate of the robot in meters
            z (float): The z coordinate of the robot in meters
            roll (float): The roll angle of the robot in degrees
            pitch (float): The pitch angle of the robot in degrees
            yaw (float): The yaw angle of the robot in degrees
        """
        trans = math.pi / 180
        self.robot_object.move_pose(x, y, z, roll * trans, pitch * trans, yaw * trans)

    def get_cartesian(self):
        """
        This method is used to reading the robot cartesian coordinates.

        Returns:
            list: a cartesian list coordinates of the robot in meters and degrees
        """
        return self.robot_object.get_pose()

    def move_to_home(self):
        """
        This method is used to movement the robot to its home position.
        """
        self.robot_object.move_to_home_pose()

    def move_to_zero(self):
        """
        This method is used to movement the robot to its zero position.
        But in this case, it is not recommended to use it because the robot has a specific zero position.
        """
        self.robot_object.move_joints([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

    def open_gripper(self, **kwargs):
        """
        This method is used to opening the robot gripper.
        """
        self.robot_object.release_with_tool()

    def close_gripper(self, **kwargs):
        """
        This method is used to closing the robot gripper.
        """
        self.robot_object.grasp_with_tool()

    def gripper_close_percentage(self, finger_value=1, actuation_time=1):
        """
        This method is used to closing the robot gripper to a specific percentage

        Args:
            finger_value: finger value in percentage
            actuation_time: finger actuation time in seconds
        """
        ...

    def set_velocity(self, velocity):
        """
        This method is used to setting the robot velocity

        Args:
            velocity: the velocity value in m/s
        """
        self.robot_object.set_arm_max_velocity(velocity)

    def calibrate(self):
        """
        This method is used to calibration the robot.
        """
        self.robot_object.calibrate_auto()

    def go_to_sleep(self):
        """
        This method is used to robot going to sleep.
        """
        self.robot_object.go_to_sleep()

    def apply_emergency_stop(self):
        """
        This method is used to application an emergency stop to the robot.
        """
        ...
