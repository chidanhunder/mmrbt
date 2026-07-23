import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
import xacro

def generate_launch_description():
    pkg_name = 'mainbot'
    pkg_share = get_package_share_directory(pkg_name)
    
    # 1. Process the URDF
    xacro_file = os.path.join(pkg_share, 'urdf', 'mainbot.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    robot_description = {'robot_description': robot_description_config.toxml(), 'use_sim_time': True}
    
    # 2. Path to the Gazebo World
    world_file = os.path.join(pkg_share, 'worlds', 'empty.sdf')

    # 3. Robot State Publisher Node
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    # 4. Include the standard Gazebo Harmonic launch file
    # The '-r' argument tells Gazebo to start running immediately instead of paused
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

    # 5. Spawn the robot into Gazebo
    # This takes the /robot_description topic and injects it into the simulation
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'mainbot',
            '-topic', 'robot_description',
            '-x', '0.0',
            '-y', '0.0',
            '-z', '0.15' # Spawn it slightly above ground so it drops in smoothly
        ],
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher_node,
        gazebo,
        spawn_entity
    ])