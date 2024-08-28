from pyniryo import NiryoRobot
from rria_api.abstract_robot.connect_robot import ConnectRobot


class ConnectNed(ConnectRobot):
    """
    This class is used to connect and disconnect the NED robot.
    """
    def __init__(self, ip_address):
        """
        This method is used to initialize the NED robot object

        Args:
            ip_address: the ip address of the robot
        """
        self.ip_address = ip_address
        self.robot_object = None

    def connect_robot(self):
        """
        This method is used to connect the NED robot.

        Returns:
            the robot object, used to perform actions with the robot
        """
        self.robot_object = NiryoRobot(self.ip_address)
        self.robot_object.calibrate_auto()
        return self.robot_object

    def disconnect_robot(self):
        """
        This method is used to disconnect the NED robot.
        """
        self.robot_object.close_connection()
