# RRIA-API

The `rria-api` is an easy-to-use package that provides a common interface to control robots used by the 
Residence in Robotics and AI at the UFPE's informatics center.
The API currently supports the use of Kinova Gen3 lite and Niryo NED, 
this API supports a dummy robot for testing purposes.

### **Requirements**

- Python 3.9+
- Kortex API .whl package

### **Installation**
1. Install the latest `rria-api` package with `pip`:

```bash
pip install rria-api
```

### **Example**

```python
from rria_api import RobotObject, RobotEnum

# Create gen3 RobotObject
gen3_lite = RobotObject('192.168.2.10', RobotEnum.GEN3_LITE)

# Create Niryo NED RobotObject
ned = RobotObject('169.254.200.200', RobotEnum.NED)

gen3_lite.connect_robot()
ned.connect_robot()

gen3_lite.move_joints(30.0, 30.0, 30.0, 30.0, 30.0, 30.0)
ned.move_joints(30.0, 30.0, 30.0, 30.0, 30.0, 30.0)

gen3_lite.get_joints()
ned.get_joints()

gen3_lite.close_gripper()
ned.close_gripper()

gen3_lite.open_gripper()
ned.open_gripper()

gen3_lite.move_to_home()
ned.move_to_home()

gen3_lite.safe_disconnect()
ned.safe_disconnect()

```

## Contributors
If you want to contribute to the development of the `rria-api`, you can clone the repository from GitHub, 
develop your changes and submit a pull request.

To generate the documentation, you need to install the docs' dependencies and run this command:

```bash
task docs

# or

mkdocs serve # For live preview

mkdocs build # For build the documentation

```