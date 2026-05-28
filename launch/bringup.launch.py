import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
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
    world_file = os.path.join(pkg_share, 'worlds', 'empty.sdf')
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'urdf_config.rviz')
    slam_params_file = os.path.join(pkg_share, 'config', 'slam.yaml')
    nav2_params_file = os.path.join(pkg_share, 'config', 'nav2_params.yaml')

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
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
            '/world/empty/model/mainbot/joint_state@sensor_msgs/msg/JointState[gz.msgs.Model',
            
            # --- CÁC TOPIC MỚI BỔ SUNG CHO NAVIGATION & SLAM ---
            # Nhận lệnh điều tốc từ ROS 2 chuyển vào Gazebo (hướng đi vào: ] )
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            # Gửi dữ liệu đo đạc quãng đường từ Gazebo ra ROS 2 (hướng đi ra: [ )
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            # Gửi dữ liệu TF động (odom -> base_footprint) từ Gazebo ra ROS 2
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V'
        ],
        remappings=[
            ('/world/empty/model/mainbot/joint_state', '/joint_states'),
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

    return LaunchDescription([
        set_use_sim_time,
        robot_state_publisher_node,
        gazebo,
        spawn_entity,
        bridge,
        rviz_node,
        slam_launch,
        nav2_launch
        #velocity_smoother_node  # <--- Bổ sung dòng này
    ])
     
    