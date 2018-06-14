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

        self.rot = euler_to_rot_quat(
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
        ax.plot3D(*pos_quats_to_plot_coords(self.rect_drawable),
            color='#55bbff')
        self.coordinate_generator.draw(ax)

    def update(self, dt):
        self.motor_phi.update(dt)
        self.motor_th .update(dt)

        self.rot = euler_to_rot_quat(
            self.motor_phi.position,
            self.motor_th.position)

        self.coordinate_generator.update(dt, self.rot)

        phi_vel, th_vel = self._get_next_velocity(dt)
        self.motor_phi.set_velocity_setpoint(phi_vel)
        self.motor_th .set_velocity_setpoint(th_vel)

        self.rect_drawable = apply_rotation(self._rect_drawable_orig, self.rot)

    def _get_next_velocity(self, dt):
        """Determine next setpoint velocities of motors."""

        curr_quat = apply_rotation(np.quaternion(0, 1, 0, 0), self.rot)
        dest_quat = self.coordinate_generator.dest_quat

        curr = pos_quat_to_euler(curr_quat)
        dest = pos_quat_to_euler(dest_quat)
        # print(curr, dest)

        # TODO PID (control algo)... or should it be handled closer to motors?
        # TODO Path planning
        # TODO Velocity-accel curve to estimate time required to get to point
        #       - Cache its integral and use as lookup to estimate if we can get
        #         to point without overshoot

        # TODO should these be position or rotation quats...?
        # dist = quaternion.rotation_intrinsic_distance(curr_quat, dest_quat)
        # t_total = dist / (Motor.VEL_MAX / 2)
        # dq = quaternion.slerp_evaluate(curr_quat, dest_quat, dt / t_total)
        # dest = pos_quat_to_euler(dq)

        # TODO OK next step:
        # Figure out how to deal with motor inertia
        # So...
        # integrate?
        # cap the movement speed using this?
        # dist in e.g. phi direction?

        dist_phi = np.abs(dest[0] - curr[0])
        dist_th  = np.abs(dest[1] - curr[1])

        # less than? shouldn't this be a calculation, not some weird condition
        # maybe with a max/min or whatever()
        # if dist_phi <

        # seems like (linear?) optimization problem...?
        # "find maximum velocity given dist" #, v_init"
        phi_vel = self.motor_phi.recommend_velocity(dest[0])
        th_vel  = self.motor_th .recommend_velocity(dest[1])

        # dt = 1 / 4.0
        # dt = t_total
        # phi_vel = shortest_rad(curr[0], dest[0]) / dt
        # th_vel  = shortest_rad(curr[1], dest[1]) / dt

        # TODO why is this always 0.05 (which is dt)? neat, I guess
        # print(quaternion.rotation_intrinsic_distance(curr_quat, dq))

        return phi_vel, th_vel

