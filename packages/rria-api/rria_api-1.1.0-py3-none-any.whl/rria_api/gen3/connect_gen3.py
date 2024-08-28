from rria_api.abstract_robot.connect_robot import ConnectRobot
from rria_api.gen3.api_gen3.device_connection import DeviceConnection


class ConnectGen3(ConnectRobot):
    """
    This class is used to connect and disconnect the Gen3 robot.

    """
    route = None

    def __init__(self, ip_address, credentials):
        """
        This method is used to initialize the Gen3 robot connection.

        Args:
            ip_address: The IP address of the robot
            credentials: The credentials of the robot
        """
        self.ip_address = ip_address
        self.credentials = credentials

        self.connect_instance = DeviceConnection(ip_address=self.ip_address,
                                                 credentials=(credentials[0], credentials[1]))

    def connect_robot(self):
        """
        This method is used to connect to the robot.

        Returns:
            the route to the robot if the connection is successful
        """
        self.route = self.connect_instance.connect()

        return self.route

    def disconnect_robot(self):
        """
        Disconnect from the robot.
        """
        self.connect_instance = self.connect_instance.disconnect()
