MAINBOT - Mecanum Mobile Robot
1. Environment & System Information

    Operating System: Ubuntu 24.04 LTS.

    ROS 2 Version: Jazzy Jalisco.

    Simulation Engine: Gazebo Harmonic (ros_gz_sim).

    Workspace: ~/mmrbt.

    Package Name: mainbot (ament_cmake format).

2. Hardware Specs
Base

    Shape: Rectangular box 350 x 300 x 250 mm.

    Mass: 20.0 kg.

    Ground Clearance: 50 mm.

    Mounting Coordinates (offset from base_link): x = 0.20, y = 0.23, z = -0.095.

Drivetrain (4 Mecanum Wheels)

    Dimensions: Radius R = 0.05 m, Width L = 0.05 m.

    Standard Mass: 1.0 kg / wheel.

Sensors

    2D LiDAR: Uses gpu_lidar plugin, 360-degree FOV, range 0.12 m - 10.0 m. Mounted at xyz="0.15 0 0.15".

3. Critical Design Rules

    3D Mesh Rule: The use_mesh variable must always be set to false. The robot is rendered using <cylinder> and <box>.

    Collision Rule: The <collision> tag of the wheels must strictly use a <sphere radius="${wheel_radius}"> shape to prevent sharp edge errors causing jerky movements.

    Mecanum Kinematics Rule (X-Shape): The friction direction vector <fdir1> of the 4 wheels must form an X shape for the robot to strafe correctly.

        Front-Left (FL) & Rear-Right (RR): 1 -1 0

        Front-Right (FR) & Rear-Left (RL): 1 1 0

    Traction & Anti-Slip Rule (ABS): Wheel joints (<joint>) must have <dynamics damping="0.1" friction="0.1"/> and an effort limit <limit effort="15.0".../>.

    Gazebo Harmonic Friction Rule: <mu1>2.0</mu1>, <mu2>0.05</mu2> (Do not set mu2 = 0.0 to avoid solver errors). Mandatory syntax: <fdir1 gz:expressed_in="${parent}">${fdir}</fdir1>.

4. Current Control & Navigation Structure

    Topic Bridge (ros_gz_bridge): Data bridge for /scan, /camera/image_raw, joint_states, /odom, /tf (Gazebo -> ROS), /cmd_vel (ROS -> Gazebo).

    Navigation (Nav2): Integrates the nav2_bringup package. The local planner (DWBLocalPlanner) has optimized parameters for omnidirectional vehicles: vy_samples > 0 and max_vel_y = 0.45, allowing lateral sliding to avoid obstacles.

5. Directory Structure
Plaintext

        ~/mmrbt/src/mainbot/
        ├── CMakeLists.txt         
        ├── package.xml
        ├── config/
        |   ├── nav2.yaml
        |   ├── efk.yaml
        │   └── slam.yaml          
        ├── launch/
        │   ├── bringup.launch.py
        │   ├── gazebo.launch.py
        │   ├── mapping.launch.py  
        │   └── slam.launch.py     
        ├── maps/                  
        ├── rviz/
        │   └── urdf_config.rviz    
        ├── urdf/
        │   ├── base/base.urdf.xacro
        │   ├── wheels/mecanum_wheel.urdf.xacro
        │   ├── sensors/
        │       ├── lidar.urdf.xacro
        │       └── imu.urdf.xacro
        │   └── mainbot.urdf.xacro plugins
        └── worlds/
            ├── demo.sdf
            └── empty.sdf          

6. Setup & Execution

    Note: Gitclone to clone this git to your computer:

        mkdir -p ~/mmrbt
        cd ~/mmrbt   
        git clone https://github.com/chidanhunder/mmrbt.git

 To run directly gazebo and rviz:


    cd ~/mmrbt  
    colcon build --symlink-install  
    source install/setup.bash  
    ros2 launch mainbot bringup.launch.py  

 Open control for robot ( use /cmd_vel )    
 
    ros2 run teleop_twist_keyboard teleop_twist_keyboard
        
