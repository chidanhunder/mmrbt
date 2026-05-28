import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_name = 'mainbot'
    pkg_dir = get_package_share_directory(pkg_name)
    
    slam_config_file = os.path.join(pkg_dir, 'config', 'slam_toolbox.yaml')

    # Khởi chạy node SLAM Toolbox bất đồng bộ tương tự RB-Kairos[cite: 1]
    start_async_slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            slam_config_file,
            {'use_sim_time': True}
        ]
    )

    return LaunchDescription([
        start_async_slam_toolbox_node
    ])