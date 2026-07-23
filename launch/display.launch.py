import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    # 1. Define package name and paths
    pkg_name = 'mainbot'
    pkg_share = get_package_share_directory(pkg_name)
    
    # Path to your master URDF/Xacro file
    xacro_file = os.path.join(pkg_share, 'urdf', 'mainbot.urdf.xacro')
    
    # Path to your RViz config (we will create this later, but we define the path now)
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'urdf_config.rviz')

    # 2. Process the Xacro file into a standard URDF string
    robot_description_config = xacro.process_file(xacro_file)
    robot_description = {'robot_description': robot_description_config.toxml()}

    # 3. Define the nodes we want to run
    # Robot State Publisher: Broadcasts the robot's link positions (TFs)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    # Joint State Publisher GUI: Gives you a pop-up window with sliders to manually spin your wheels!
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui'
    )

    # RViz2: The 3D visualizer
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file] if os.path.exists(rviz_config_file) else []
    )

    # 4. Launch them all
    return LaunchDescription([
        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node
    ])