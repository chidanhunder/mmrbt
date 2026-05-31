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

    # 3. Nodes
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[robot_description]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': f'-r {world_file}'}.items()
    )

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

    # 4. Bridge: Chuyển dữ liệu giữa Gazebo và ROS 2
    # Khởi chạy ROS-Gazebo Bridge
    # 4. Bridge: Chuyển dữ liệu giữa Gazebo và ROS 2
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{'use_sim_time': True}],
        arguments=[
            #'/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            #'/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V', # <--- [QUAN TRỌNG]: THÊM DẤU PHẨY TẠI ĐÂY
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
            '/imu/data@sensor_msgs/msg/Imu[gz.msgs.IMU',
        ],
        output='screen'
    )
    # 6. SLAM Toolbox
    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('slam_toolbox'), 'launch', 'online_async_launch.py')
        ]),
        launch_arguments={
            'slam_params_file': slam_params_file,
            'use_sim_time': 'true'
        }.items()
    )

    # 5. RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file],
        parameters=[{'use_sim_time': True}]
    )
    #nav2
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(get_package_share_directory('nav2_bringup'), 'launch', 'navigation_launch.py')
        ]),
        launch_arguments={
            'params_file': nav2_params_file,
            'use_sim_time': 'true',
            'autostart': 'true'
        }.items()
    )
    #ekf
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_config_file, {'use_sim_time': True}]
    )

    return LaunchDescription([
        set_use_sim_time,
        robot_state_publisher_node,
        gazebo,
        spawn_entity,
        bridge,
        rviz_node,
        slam_launch,
        nav2_launch,
        ekf_node,
    ])
    