#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math

class VelocitySmoother(Node):
    def __init__(self):
        super().__init__('velocity_smoother')

        # 1. Khai báo các tham số gia tốc tối đa (m/s^2 và rad/s^2)
        # Khung gầm 20kg nên để gia tốc vừa phải để tránh lết bánh
        self.declare_parameter('accel_x', 0.5)      # Tiến/lùi
        self.declare_parameter('accel_y', 0.5)      # Trượt ngang (Strafing)
        self.declare_parameter('accel_theta', 1.0)  # Xoay tại chỗ
        self.declare_parameter('frequency', 50.0)   # Tần số cập nhật 50Hz

        self.a_x = self.get_parameter('accel_x').value
        self.a_y = self.get_parameter('accel_y').value
        self.a_theta = self.get_parameter('accel_theta').value
        self.dt = 1.0 / self.get_parameter('frequency').value

        # Biến lưu trữ trạng thái
        self.target_vel = Twist()
        self.current_vel = Twist()

        # 2. Khởi tạo Subscriber và Publisher
        self.sub = self.create_subscription(Twist, 'cmd_vel_raw', self.target_cb, 10)
        self.pub = self.create_publisher(Twist, 'cmd_vel', 10)
        
        # 3. Khởi tạo Timer chạy vòng lặp nội suy
        self.timer = self.create_timer(self.dt, self.timer_cb)
        self.get_logger().info('Velocity Smoother Node has been started.')

    def target_cb(self, msg):
        # Cập nhật vận tốc mục tiêu từ bàn phím/joystick
        self.target_vel = msg

    def smooth_value(self, current, target, accel):
        # Tính toán bước nhảy vận tốc tối đa trong 1 chu kỳ (dt)
        max_step = accel * self.dt
        diff = target - current
        
        # Nếu khoảng cách đến mục tiêu lớn hơn bước nhảy, thì nhích từ từ
        if abs(diff) > max_step:
            return current + math.copysign(max_step, diff)
        # Nếu đã ở rất gần mục tiêu, gán bằng mục tiêu luôn
        else:
            return target

    def timer_cb(self):
        # Nội suy từng trục tọa độ
        self.current_vel.linear.x = self.smooth_value(self.current_vel.linear.x, self.target_vel.linear.x, self.a_x)
        self.current_vel.linear.y = self.smooth_value(self.current_vel.linear.y, self.target_vel.linear.y, self.a_y)
        self.current_vel.angular.z = self.smooth_value(self.current_vel.angular.z, self.target_vel.angular.z, self.a_theta)
        
        # Xuất lệnh đã làm mượt ra cho Gazebo
        self.pub.publish(self.current_vel)

def main(args=None):
    rclpy.init(args=args)
    node = VelocitySmoother()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()