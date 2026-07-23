import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction 
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import SetParameter
import xacro

def generate_launch_description():
    pkg_name = 'mainbot'
    pkg_share = get_package_share_directory(pkg_name)
    set_use_sim_time = SetParameter(name='use_sim_time', value=True)
    # 1. Process the URDF
    xacro_file = os.path.join(pkg_share, 'urdf', 'mainbot.urdf.xacro')
    robot_description_config = xacro.process_file(xacro_file)
    robot_description = {'robot_description': robot_description_config.toxml(), 'use_sim_time': True}
    
    # 2. File Paths
    world_file = os.path.join(pkg_share, 'worlds', 'demo.sdf')
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'urdf_config.rviz')
    slam_params_file = os.path.join(pkg_share, 'config', 'slam.yaml')
    nav2_params_file = os.path.join(pkg_share, 'config', 'nav2_params.yaml')
    ekf_config_file = os.path.join(pkg_share, 'config', 'ekf.yaml')
    laser_filter_config = os.path.join(pkg_share, 'config', 'laser_filter_params.yaml')

    # ============================================================
    # 3. Core Nodes (launch in dependency order)
    # ============================================================

    # 3a. Robot State Publisher — publishes URDF TF tree
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    # 3b. Gazebo Simulator
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r --physics-engine gz-physics-bullet-featherstone-plugin {world_file}'}.items()
    )

    # 3c. Spawn robot into Gazebo
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'mainbot',
            '-topic', 'robot_description',
            '-x', '0.0', '-y', '0.0', '-z', '0.15'
        ],
        output='screen'
    )

    # 3d. ROS-Gazebo Bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'use_sim_time': False}], # MUST BE FALSE for the bridge that publishes /clock
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU',
        ],
        remappings=[
            ('/odom', '/odom/unfiltered')
        ],
        output='screen'
    )

    # ============================================================
    # 4. Sensor Processing
    # ============================================================

    # 4a. Laser filter — removes self-scan points from LiDAR data
    laser_filter_node = Node(
        package='laser_filters',
        executable='scan_to_scan_filter_chain',
        name='scan_filter',
        output='screen',
        parameters=[laser_filter_config, {'use_sim_time': True}],
        remappings=[
            ('/scan', '/scan'),
            ('/scan_filtered', '/scan_filtered')
        ]
    )

    # ============================================================
    # 5. Localization (delayed to wait for Gazebo + Bridge)
    # ============================================================

    # 5a. EKF — fuses odom + IMU, publishes /odometry/filtered
    #     TF publishing ENABLED (EKF owns odom->base_footprint TF, Mecanum Drive TF is disabled)
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config_file, {'use_sim_time': True}],
        remappings=[('/odometry/filtered', '/odom')]
    )

    # 5b. SLAM Toolbox — builds map from LiDAR, publishes map->odom TF
    slam_launch = TimerAction(
        period=5.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    os.path.join(get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')
                ]),
                launch_arguments={
                    'slam_params_file': slam_params_file,
                    'use_sim_time': 'true'
                }.items()
            )
        ]
    )

    # ============================================================
    # 6. Navigation (delayed further to wait for SLAM map)
    # ============================================================

    # 6a. Nav2 — path planning + following using live SLAM map
    nav2_launch = TimerAction(
        period=10.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource([
                    os.path.join(get_package_share_directory('nav2_bringup'), 'launch', 'navigation_launch.py')
                ]),
                launch_arguments={
                    'params_file': nav2_params_file,
                    'use_sim_time': 'true',
                    'autostart': 'false',
                }.items()
            )
        ]
    )

    # ============================================================
    # 7. Visualization
    # ============================================================

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        set_use_sim_time,
        gazebo,
        spawn_entity,
        bridge,
        robot_state_publisher_node,
        ekf_node,
        laser_filter_node,
        slam_launch,
        nav2_launch,
        rviz_node,
    ])