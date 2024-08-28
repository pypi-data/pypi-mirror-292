from rria_api.abstract_robot.action_robot import ActionRobot


class ActionDummy(ActionRobot):
    def move_joints(self, j1, j2, j3, j4, j5, j6):
        """
        This dummy method is used to simulate the movement of the robot joints.
        Args:
            j1 (float): the angle of the first joint in degrees
            j2 (float): the angle of the second joint in degrees
            j3 (float): the angle of the third joint in degrees
            j4 (float): the angle of the fourth joint in degrees
            j5 (float): the angle of the fifth joint in degrees
            j6 (float): the angle of the sixth joint in degrees

        Returns:

        """
        ...

    def get_joints(self):
        """
        This dummy method is used to simulate the reading of the robot joints.

        Returns:
            list: an angles list of the robot joints in degrees
        """
        return [0, 0, 0, 0, 0, 0]

    def move_cartesian(self, x, y, z, roll, pitch, yaw):
        """
        This dummy method is used to simulate the movement of the robot in cartesian space.

        Args:
            x (float): The x coordinate of the robot in meters
            y (float): The y coordinate of the robot in meters
            z (float): The z coordinate of the robot in meters
            roll (float): The roll angle of the robot in degrees
            pitch (float): The pitch angle of the robot in degrees
            yaw (float): The yaw angle of the robot in degrees
        """
        ...

    def get_cartesian(self):
        """
        This dummy method is used to simulate the reading of the robot cartesian coordinates.

        Returns:
            list: a cartesian list coordinates of the robot in meters and degrees
        """
        return [0, 0, 0, 0, 0, 0]

    def move_to_home(self):
        """
        This dummy method is used to simulate the movement of the robot to its home position.
        """
        ...

    def move_to_zero(self):
        """
        This dummy method is used to simulate the movement of the robot to its zero position.
        """
        ...

    def open_gripper(self, execution_time=1):
        """
        This dummy method is used to simulate the opening of the robot gripper.

        Args:
            execution_time: execution time in seconds
        """
        ...

    def close_gripper(self, execution_time=1):
        """
        This dummy method is used to simulate the closing of the robot gripper.

        Args:
            execution_time: execution time in seconds
        """
        ...

    def gripper_close_percentage(self, finger_value=1, actuation_time=1):
        """
        This dummy method is used to simulate the closing of the robot gripper to a specific percentage

        Args:
            finger_value: finger value in percentage
            actuation_time: finger actuation time in seconds
        """
        ...

    def set_velocity(self, velocity):
        """
        This dummy method is used to simulate the setting of the robot velocity

        Args:
            velocity: the velocity value in m/s

        """
        ...

    def calibrate(self):
        """
        This dummy method is used to simulate the calibration of the robot.
        """
        ...

    def go_to_sleep(self):
        """
        This dummy method is used to simulate the robot going to sleep.
        """
        ...

    def apply_emergency_stop(self):
        """
        This dummy method is used to simulate the application of an emergency stop to the robot.
        """
        ...