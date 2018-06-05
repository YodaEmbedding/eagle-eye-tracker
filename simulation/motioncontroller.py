import numpy as np
import quaternion

from coordinategenerator import CoordinateGenerator
from coordinatemath import *
from motor import Motor

class MotionController:
    def __init__(self):
        self.coordinate_generator = CoordinateGenerator()

        # Current position in Euler angles
        # Consider storing current position as a quaternion as well...?
        self.motor_phi = Motor()
        self.motor_th  = Motor()

        # self.rot = euler_to_quat(
        #     self.motor_phi.position,
        #     self.motor_th.position)

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
        ax.plot3D(*quats_to_plot_coords(self.rect_drawable), color='#55bbff')
        self.coordinate_generator.draw(ax)

    # TODO time delays, inertia, etc?
    def update(self, dt):
        self.motor_phi.update(dt)
        self.motor_th .update(dt)

        self.rot = euler_to_quat(
            self.motor_phi.position,
            self.motor_th.position)

        self.coordinate_generator.update(dt, self.rot)
        coord = self.coordinate_generator.coord
        dest  = self.coordinate_generator.dest_quat
        euler = quat_to_euler(dest)

        print(dest)
        print(euler)

        # TODO determine position setpoint (dphi, dth) by understanding geometry
        # determine velocity setpoint using PID controller on position setpoint
        # change this to depend on quaternion?
        phi_pwr = 10000 * coord[0]
        th_pwr  = 10000 * coord[1]

        self.motor_phi.set_velocity_setpoint(phi_pwr)
        self.motor_th .set_velocity_setpoint(th_pwr)

        self.rect_drawable = apply_rotation(self._rect_drawable_orig, self.rot)

