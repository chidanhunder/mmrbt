# [cite_start]MAINBOT - Mecanum Mobile Robot [cite: 1]

## [cite_start]1. Thông tin Môi trường & Hệ thống [cite: 2]
* [cite_start]**Hệ điều hành**: Ubuntu 24.04 LTS[cite: 2].
* [cite_start]**Phiên bản ROS 2**: Jazzy Jalisco[cite: 2].
* [cite_start]**Engine Mô phỏng**: Gazebo Harmonic (`ros_gz_sim`)[cite: 2].
* [cite_start]**Không gian làm việc (Workspace)**: `~/mmrbt`[cite: 2].
* [cite_start]**Tên gói**: `mainbot` (Dạng ament_cmake)[cite: 2].

---

## 2. Thông số Kỹ thuật Vật lý (Hardware Specs)

### Khung gầm (Base)
* [cite_start]**Hình dáng**: Hình hộp chữ nhật $450 \times 400 \times 250$ mm[cite: 3].
* [cite_start]**Khối lượng**: $20.0$ kg[cite: 4].
* [cite_start]**Khoảng sáng gầm**: $50$ mm[cite: 4].
* [cite_start]**Tọa độ gắn (offset so với base_link)**: x = 0.20, y = 0.23, z = -0.095[cite: 5].

### [cite_start]Hệ truyền động (4 bánh Mecanum) [cite: 4]
* [cite_start]**Kích thước**: Bán kính $R = 0.08$ m, Bề rộng $L = 0.05$ m[cite: 4].
* **Khối lượng chuẩn**: $1.0$ kg / bánh[cite: 5].

### Cảm biến (Sensors)
* [cite_start]**LiDAR 2D**: Dùng plugin `gpu_lidar`, góc quét 360 độ, tầm nhìn $0.12$m - $10.0$m[cite: 5]. [cite_start]Gắn tại xyz="0.15 0 0.15"[cite: 6].
* **Camera RGB**: Phân giải $640 \times 480$. [cite_start]Gắn tại xyz="0.23 0 0.10"[cite: 6].

---

## [cite_start]3. Các Quy tắc Thiết kế Cốt lõi (Critical Rules) [cite: 7]
* [cite_start]**Quy tắc Mesh 3D**: Biến `use_mesh` phải luôn để `false`[cite: 7]. [cite_start]Robot render bằng `<cylinder>` và `<box>`[cite: 8].
* **Quy tắc Collision**: Thẻ `<collision>` của bánh xe bắt buộc dùng hình `<sphere radius="${wheel_radius}">` để chống lỗi viền sắc cạnh gây giật cục[cite: 8].
* [cite_start]**Quy tắc Động học Mecanum (Chữ X)**: Vector hướng ma sát `<fdir1>` của 4 bánh phải tạo thành hình chữ X để robot trượt ngang đúng chuẩn[cite: 8]. [cite_start]Bánh Trước-Trái (FL) & Sau-Phải (RR) = 1 -1 0[cite: 8]. [cite_start]Bánh Trước-Phải (FR) & Sau-Trái (RL) = 1 1 0[cite: 8].
* [cite_start]**Quy tắc Bám đường & Chống lết bánh (ABS)**: Khớp bánh xe (`<joint>`) phải có `<dynamics damping="0.1" friction="0.1"/>` và giới hạn mô-men xoắn `<limit effort="15.0".../>`[cite: 9].
* **Quy tắc Ma sát Gazebo Harmonic**: `<mu1>2.0</mu1>`, `<mu2>0.05</mu2>` (Không để mu2 = 0.0 để tránh lỗi solver)[cite: 9]. Cú pháp bắt buộc: `<fdir1 gz:expressed_in="${parent}">${fdir}</fdir1>`[cite: 9].

---

## 4. Cấu trúc Điều khiển & Điều hướng Hiện tại
* [cite_start]**Dịch topic (`ros_gz_bridge`)**: Cầu nối dữ liệu `/scan`, `/camera/image_raw`, `joint_states`, `/odom`, `/tf` (Gazebo -> ROS), `/cmd_vel` (ROS -> Gazebo)[cite: 10].
* **Điều hướng (Nav2)**: Tích hợp gói `nav2_bringup`[cite: 11]. Bộ quy hoạch cục bộ (`DWBLocalPlanner`) có thông số tối ưu cho xe đa hướng: `vy_samples > 0` và `max_vel_y = 0.45`, cho phép trượt ngang né vật cản[cite: 11].
## 2. Cấu trúc Thư mục (Directory Structure)
```text
~/mmrbt/src/mainbot/
├── CMakeLists.txt         # Đã thêm rule install cho config/ và maps/
├── package.xml
├── config/
│   └── slam.yaml          # Cấu hình SLAM Toolbox cho robot mecanum
├── launch/
│   ├── bringup.launch.py  # RViz, Gazebo, Robot State Pub, Bridge
│   └── slam.launch.py     # Khởi chạy SLAM Toolbox + ép use_sim_time
├── maps/                  # Chứa file bản đồ .yaml và .pgm sau khi lưu
├── rviz/
│   └── urdf_config.rviz   # Đã cấu hình đúng QoS cho Map, LiDAR, Camera
├── urdf/
│   ├── base/base.urdf.xacro
│   ├── wheels/mecanum_wheel.urdf.xacro
│   ├── sensors/lidar.urdf.xacro & camera.urdf.xacro
│   └── mainbot.urdf.xacro # File lắp ráp tổng, chứa các plugin Gazebo
└── worlds/
    └── empty.sdf          # Đã chèn plugin render engine ogre2