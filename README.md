    # MAINBOT - Mecanum Mobile Robot

## 1. Thông tin Môi trường & Hệ thống
* **Hệ điều hành**: Ubuntu 24.04 LTS
* **Phiên bản ROS 2**: Jazzy Jalisco
* **Engine Mô phỏng**: Gazebo Harmonic
* **Không gian làm việc (Workspace)**: `~/mmrbt`
* **Tên gói (Package Name)**: `mainbot`

---

## 2. Cấu trúc Thư mục (Directory Structure)
```text
~/mmrbt/src/mainbot/
├── CMakeLists.txt         
├── package.xml
├── config/
│   └── slam.yaml          
├── launch/
│   ├── bringup.launch.py  
│   └── slam.launch.py     
├── maps/                  
├── rviz/
│   └── urdf_config.rviz   
├── urdf/
│   ├── base/base.urdf.xacro
│   ├── wheels/mecanum_wheel.urdf.xacro
│   ├── sensors/lidar.urdf.xacro & camera.urdf.xacro
│   └── mainbot.urdf.xacro 
└── worlds/
    └── empty.sdf          