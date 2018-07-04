import numpy as np
import quaternion

from .coordinategenerator import CoordinateGenerator
from .coordinatemath import *
from .motor import Motor

class MotionController:
    """Controls motors to move to desired position as fast as possible."""

    def __init__(self):
        self.coordinate_generator = CoordinateGenerator()

        self.motor_phi = Motor(velocity_max=3.0, accel_max=1.5)
        self.motor_th  = Motor(velocity_max=3.0, accel_max=1.5)

        self.curr_rot = euler_to_rot_quat(
            self.motor_phi.position,
            self.motor_th.position)

        r = self.curr_rot
        self.prev_rot = r
        self.prev_dest_rot = r
        self.dest_rot = r

        # TODO we really need to come up with a better convention for "position"
        # vs "rotation" quaternion...
        q = rot_quat_to_pos_quat(self.curr_rot)
        self.prev_quat = q
        self.curr_quat = q
        self.prev_dest_quat = q
        self.dest_quat = q

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
        self.rect_drawable = apply_rotation(self._rect_drawable_orig, self.curr_rot)

    def draw(self, ax):
        """Draw tracker camera."""
        ax.plot3D(*pos_quats_to_plot_coords(self.rect_drawable),
            color='#55bbff')
        self.coordinate_generator.draw(ax)

    def update(self, dt):
        self.motor_phi.update(dt)
        self.motor_th .update(dt)

        self.prev_rot = self.curr_rot
        self.curr_rot = euler_to_rot_quat(
            self.motor_phi.position,
            self.motor_th .position)

        self.coordinate_generator.update(dt, self.curr_rot)

        self.prev_dest_rot = self.dest_rot
        self.dest_rot = pos_quat_to_rot_quat(self.coordinate_generator.dest_quat)

        self.prev_quat = self.curr_quat
        self.curr_quat = rot_quat_to_pos_quat(self.curr_rot)
        self.prev_dest_quat = self.dest_quat
        self.dest_quat = rot_quat_to_pos_quat(self.dest_rot)

        phi_vel, th_vel = self._get_next_velocity(dt)
        self.motor_phi.set_velocity_setpoint(phi_vel)
        self.motor_th .set_velocity_setpoint(th_vel)

        self.rect_drawable = apply_rotation(self._rect_drawable_orig, self.curr_rot)

    def _get_next_velocity(self, dt):
        """Determine next setpoint velocities of motors."""

        # predict better dest, velocity at dest
        # need to keep track of current velocity too...
        # dest_quat, dest_quat_vel = self._predict_state()
        self._predict_state()

        curr = pos_quat_to_euler(self.curr_quat)
        dest = pos_quat_to_euler(self.dest_quat_predict)

        # TODO recommend_velocity to reach desired setpoint at a given velocity
        phi_vel = self.motor_phi.recommend_velocity(dest[0])
        th_vel  = self.motor_th .recommend_velocity(dest[1])

        return phi_vel, th_vel

        # TODO use this to interpolate between dest_quat and dest_predict_quat...!
        # TODO should these be position or rotation quats...?
        # dist = quaternion.rotation_intrinsic_distance(curr_quat, dest_quat)
        # t_total = dist / (Motor.VEL_MAX / 2)
        # dq = quaternion.slerp_evaluate(curr_quat, dest_quat, dt / t_total)
        # dest = pos_quat_to_euler(dq)

        # TODO PID (control algo)... or should it be handled closer to motors?
        # TODO Path planning
        # TODO Velocity-accel curve to estimate time required to get to point
        #       - Cache its integral and use as lookup to estimate if we can get
        #         to point without overshoot

        # less than? shouldn't this be a calculation, not some weird condition
        # maybe with a max/min or whatever()
        # if dist_phi <

        # seems like (linear?) optimization problem...?
        # "find maximum velocity given dist" #, v_init"

        # TODO use shortest_rad... provide deltas for destination?
        # let motor figure out which position is closest to delta?
        # motor.get_nearest_delta()

        # dt = 1 / 4.0
        # dt = t_total
        # phi_vel = shortest_rad(curr[0], dest[0]) / dt
        # th_vel  = shortest_rad(curr[1], dest[1]) / dt

        # TODO why is this always 0.05 (which is dt)? neat, I guess
        # print(quaternion.rotation_intrinsic_distance(curr_quat, dq))

    def _predict_state(self):
        # self.dest_quat_predict = self.dest_quat

        self.dest_quat_predict = extrapolate_quat(
            self.prev_dest_quat, self.dest_quat, 4.0)

        # self.dest_quat_predict = rot_quat_to_pos_quat(extrapolate_quat(
        #     self.prev_dest_rot, self.dest_rot, 2.0))

        # slerp(prev_dest_quat, dest_quat)

        # TODO use some sort of velocity through SLERP... make a separate function to estimate this?

    # TODO
    # @staticmethod
    # def _slerp_time(q1, q2, ???):

