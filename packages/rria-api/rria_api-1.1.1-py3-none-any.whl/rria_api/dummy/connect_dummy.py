from rria_api.abstract_robot.connect_robot import ConnectRobot


class ConnectDummy(ConnectRobot):
    def connect_robot(self):
        """
        This dummy method is used to simulate the connection of the robot.

        """
        return None

    def disconnect_robot(self):
        """
        This dummy method is used to simulate the disconnection of the robot.

        """
        ...
