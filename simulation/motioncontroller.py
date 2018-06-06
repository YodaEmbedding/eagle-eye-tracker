import numpy as np
import quaternion

from coordinategenerator import CoordinateGenerator
from coordinatemath import *
from motor import Motor

class MotionController:
    """Controls motors to move to desired position as fast as possible."""

    def __init__(self):
        self.coordinate_generator = CoordinateGenerator()

        self.motor_phi = Motor()
        self.motor_th  = Motor()

        self.rot = euler_to_quat(
            self.motor_phi.position,
            self.motor_th.position)

        w = self.coordinate_generator.width
        h = self.coordinate_generator.height
        self._rect_drawable_orig = np.array([
            np.quaternion(0, 1,  w,  h),  # A
            np.quaternion(0, 1, -w,  h),  # B
            np.quaternion(0, 1, -w, -h),  # C
            np.quaternion(0, 1,  w, -h),  # D
            np.quaternion(0, 1,  w,  h),  # A
            np.quaternion(0, 1, -w, -h),  # C
            np.quaternion(0, 1, -w,  h),  # B
            np.quaternion(0, 1,  w, -h),  # D
        ])

    def draw(self, ax):
        """Draw tracker camera."""
        ax.plot3D(*quats_to_plot_coords(self.rect_drawable), color='#55bbff')
        self.coordinate_generator.draw(ax)

    def update(self, dt):
        self.motor_phi.update(dt)
        self.motor_th .update(dt)

        self.rot = euler_to_quat(
            self.motor_phi.position,
            self.motor_th.position)

        self.coordinate_generator.update(dt, self.rot)

        phi_vel, th_vel = self._get_next_velocity()
        self.motor_phi.set_velocity_setpoint(phi_vel)
        self.motor_th .set_velocity_setpoint(th_vel)

        self.rect_drawable = apply_rotation(self._rect_drawable_orig, self.rot)

    def _get_next_velocity(self):
        """Determine next setpoint velocities of motors."""

        curr_quat = apply_rotation(np.quaternion(0, 1, 0, 0), self.rot)
        dest_quat = self.coordinate_generator.dest_quat

        curr = pos_quat_to_euler(curr_quat)
        dest = pos_quat_to_euler(dest_quat)
        print(curr, dest)

        phi_vel = 1 * shortest_rad(curr[0], dest[0])
        th_vel  = 1 * shortest_rad(curr[1], dest[1])

        return phi_vel, th_vel

