from rria_api.ned.action_ned import ActionNed
from rria_api.gen3.action_gen3 import ActionGen3
from rria_api.dummy.action_dummy import ActionDummy

from rria_api.ned.connect_ned import ConnectNed
from rria_api.gen3.connect_gen3 import ConnectGen3
from rria_api.dummy.connect_dummy import ConnectDummy

from rria_api.robot_enum import RobotEnum


class RobotObject:
    """
    This class is used to initialize and use the robot object.
    """
    def __init__(self, ip_address, robot_type):
        """
        This class is used to initialize and use the robot object.

        Args:
            ip_address: string with the ip address of the robot
            robot_type: enum with the type of the robot
        """
        self.ip_address = ip_address
        self.robot_type = robot_type

        self.robot_instance = None
        self.action_instance = None

        self.connection_instance = self.__get_connection_instance()

    def __get_connection_instance(self):
        """
        Get the connection instance based on the robot type

        Returns:
            Connection instance of a specific robot type

        Raises:
            ValueError: If a robot type is not found
        """
        if self.robot_type == RobotEnum.GEN3_LITE:
            connection_instance = ConnectGen3(self.ip_address, ["admin", "admin"])
            return connection_instance

        elif self.robot_type == RobotEnum.NED:
            connection_instance = ConnectNed(self.ip_address)
            return connection_instance

        elif self.robot_type == RobotEnum.DUMMY:
            connection_instance = ConnectDummy()
            return connection_instance

        else:
            raise ValueError("Robot type not found")


    def __get_action_instance(self):
        """
        Get the action instance based on the robot type

        Returns:
            Action instance of a specific robot type
        """
        if self.robot_type == RobotEnum.GEN3_LITE:
            action_instance = ActionGen3(self.robot_instance)
            return action_instance

        elif self.robot_type == RobotEnum.NED:
            action_instance = ActionNed(self.robot_instance)
            return action_instance

        elif self.robot_type == RobotEnum.DUMMY:
            action_instance = ActionDummy()
            return action_instance

    def connect_robot(self) -> bool:
        """
        Connect robot depends on the robot type

        Returns:
            True if the connection was successful, False otherwise
        """

        self.robot_instance = self.connection_instance.connect_robot()

        # Create an instance of the action class
        self.action_instance = self.__get_action_instance()

        return True

    def disconnect_robot(self):
        """
        Close connection with robot

        """
        self.connection_instance.disconnect_robot()

    def safe_disconnect(self):
        """
        Move robot for home position and close connection with robot.
        Home position dependes on a robot type.
        For Gen3 is [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] degrees and for Ned is [0.0, 0.3, -1.3, 0.0, 0.0, 0.0] radians.
        """
        self.connection_instance.disconnect_robot()

    # Move Joints/Cartesian methods
    @property
    def joints(self) -> list:
        """
        Get joints value in degrees

        Returns:
            List[float] of joints value
        """
        return self.get_joints()

    def get_joints(self) -> list:
        """
        Get joints value in degrees
        You can also use a getter

        Returns:
            List[float] of joints value

        Example:
            joints = robot.get_joints()

            joints = robot.joints
        """
        return self.action_instance.get_joints()

    def move_joints(self, j1, j2, j3, j4, j5, j6):
        """
        Move robot joints. Joints are expressed in degrees.

        All lines of the next example realize the same operation:

        Args:
            j1 (float): joint 1,
            j2 (float): joint 2,
            j3 (float): joint 3,
            j4 (float): joint 4,
            j5 (float): joint 5,
            j6 (float): joint 6,

        Example:
            robot.move_joints(0.2, 0.1, 0.3, 0.0, 0.5, 0.0)
        """
        self.action_instance.move_joints(j1, j2, j3, j4, j5, j6)

    @property
    def cartesian(self) -> list:
        """
        Get an end-effector link as [x, y, z, roll, pitch, yaw].
        Call this method is equivalent to call get_cartesian() method.

        Returns:
            Robot pose list[float].
        """
        return self.get_cartesian()

    def get_cartesian(self) -> list:
        """
        Get an end-effector link pose as [x, y, z, roll, pitch, yaw].
        x, y & z are expressed in meters / roll, pitch & yaw are expressed in degrees from Gen3 Lite
        and radians from Ned.

        You can also use a getter

        Returns:
            Robot pose list[float].

        Examples:
            joints = robot.get_cartesian()

            joints = robot.cartesian
        """
        return self.action_instance.get_cartesian()

    def move_cartesian(self, x, y, z, roll, pitch, yaw):
        """
        Move robot end effector pose to a (x, y, z, roll, pitch, yaw, frame_name) pose
        in a particular frame (frame_name) if defined.
        x, y & z are expressed in meters / roll, pitch & yaw are expressed in degrees.

        All lines of the next example realize the same operation: ::

        Args:
            x (float): coordinate x,
            y (float): coordinate y,
            z (float): coordinate z,
            roll (float): rotation on x-axis,
            pitch (float): rotation on y-axis,
            yaw (float): rotation on z-axis,

        Example:
            robot.move_cartesian(0.2, 0.1, 0.3, 0.0, 0.5, 0.0)

        """
        return self.action_instance.move_cartesian(x, y, z, roll, pitch, yaw)


    # TODO: Pegar os valores de home do robot
    def move_to_home(self):
        """
        Move robot for home position.
        Home position dependes on a robot type.
        For Gen3 is [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        degrees and for Ned is [0.0, 0.3, -1.3, 0.0, 0.0, 0.0] radians.

        """
        self.action_instance.move_to_home()


    def move_to_zero(self):
        """
        Move the robot to zero positions.
        Home position dependes on a robot type.
        For Gen3 is [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        degrees and for Ned is [0.0, 0.0, 0.0, 0.0, 0.0, 0.0] degrees.
        """
        self.action_instance.move_to_zero()


    def gripper_close_percentage(self, actuation_time=2, finger_value=None):
        """
        Close gripper with a percentage of the maximum opening. If gen3_lite is being used, it is possible to control

        Args:
            actuation_time: If gen3_lite is being used, it is possible to control the motor actuation time,
            to be able to partially open the gripper
            finger_value: If gen3_lite is being used, it is possible to control the opening percentage
            of the actuator. Supports a value between 0 and 1, where values closer to 0 are closer to the actuator's
            open state.

        """
        self.action_instance.gripper_close_percentage(finger_value=finger_value, actuation_time=actuation_time)


    def open_gripper(self, actuation_time=2):
        """
        Fully open gripper.

        Args:
            actuation_time (float): If gen3_lite is being used, it is possible to control the motor actuation time,
            to be able to partially open the gripper

        """
        self.action_instance.open_gripper(actuation_time)

    def close_gripper(self, actuation_time=2):
        """
        Fully close gripper.

        Args:
            actuation_time: If gen3_lite is being used, it is possible to control the motor actuation time, to be able to partially close the gripper
        """
        self.action_instance.close_gripper(actuation_time)


    # TODO: Ver a função de aumento de velocidade para o Gen3
    def set_velocity(self, velocity):
        """
        Limit arm max velocity to a percentage of its maximum velocity. For Niryo one, velocity is a percentage of 100.
        For gen3, there are two types of velocities, an angular and a cartesian. The speed used in this method is
        angular.

        Args:
            velocity (int): Should be between 1 & 100 for niryo

        """
        self.action_instance.set_velocity(velocity)


    def calibrate(self):
        """
        Start an automatic motors calibration if motors are not calibrated yet
        """
        self.action_instance.calibrate()


    def go_to_sleep(self):
        """
        Go home pose and activate learning mode. The function is available only for Ned robot.
        """
        self.action_instance.go_to_sleep()

    def apply_emergency_stop(self):
        """
        Apply emergency stop. The function is available only for Kinova Gen3.
        """
        self.action_instance.apply_emergency_stop()
