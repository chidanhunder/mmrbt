import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_name = 'mainbot'
    
    # Đường dẫn đến file config YAML
    slam_config_file = PathJoinSubstitution([
        FindPackageShare(pkg_name),
        'config',
        'slam.yaml'
    ])

    # Kéo launch file online_async mặc định của slam_toolbox
    slam_toolbox_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                FindPackageShare('slam_toolbox'),
                'launch',
                'online_async_launch.py'
            ])
        ]),
        launch_arguments={'slam_params_file': slam_config_file}.items()
    )

    return LaunchDescription([
        slam_toolbox_launch
    ])