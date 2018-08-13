import numpy as np
import quaternion

from .coordinatemath import (apply_rotation, euler_to_rot_quat,
    pos_quat_to_euler, pos_quats_to_plot_coords, rot_quat_to_pos_quat)

class MotionController:
    """Controls motors to move to desired position as fast as possible."""

    def __init__(self, coordinate_generator, motor_phi, motor_th,
        latency_compensation=0.0):

        self.coordinate_generator = coordinate_generator
        self.motor_phi = motor_phi
        self.motor_th  = motor_th
        self.latency_compensation = latency_compensation

        self.curr_rot = euler_to_rot_quat(
            self.motor_phi.position,
            self.motor_th.position)

        # TODO we really need to come up with a better convention for "position"
        # vs "rotation" quaternion...
        q = rot_quat_to_pos_quat(self.curr_rot)
        self.prev_quat = q
        self.curr_quat = q
        self.prev_dest_quat = q
        self.dest_quat = q
        self.dest_quat_predict = q

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
        self.rect_drawable = apply_rotation(self._rect_drawable_orig,
            self.curr_rot)

    def draw(self, ax):
        """Draw tracker camera."""
        ax.plot3D(*pos_quats_to_plot_coords(self.rect_drawable),
            color='#55bbff')
        ax.scatter3D(*pos_quats_to_plot_coords([self.dest_quat]),
            s=50, color='#ffffff')
        self.coordinate_generator.draw(ax)

    def update(self, dt):
        self.motor_phi.update(dt)
        self.motor_th .update(dt)

        self.curr_rot = euler_to_rot_quat(
            self.motor_phi.position,
            self.motor_th .position)

        self.latent_rot = euler_to_rot_quat(
            self.motor_phi.position_history.get(self.latency_compensation),
            self.motor_th .position_history.get(self.latency_compensation))

        # TODO
        # consider faded dot as what is shown,
        # but use corrected position to estimate location of dot (in the past)
        self.coordinate_generator.update(dt, self.latent_rot)

        self._update_quats()
        self._set_velocity_setpoints()

        self.rect_drawable = apply_rotation(self._rect_drawable_orig,
            self.curr_rot)

    def _get_next_velocity(self):
        """Determine next setpoint velocities of motors."""

        self._predict_state()

        # curr = pos_quat_to_euler(self.curr_quat)
        dest = pos_quat_to_euler(self.dest_quat_predict)

        # TODO recommend_velocity to reach desired setpoint at a given velocity
        phi_vel = self.motor_phi.recommend_velocity(dest[0])
        th_vel  = self.motor_th .recommend_velocity(dest[1])

        return phi_vel, th_vel

        # TODO PID (control algo)... or should it be handled closer to motors?
        # TODO Path planning
        # TODO Velocity-accel curve to estimate time required to get to point
        #       - Cache its integral and use as lookup to estimate if we can get
        #         to point without overshoot

    def _predict_state(self):
        # TODO WRONG. Doesn't do anything useful when dt is small
        # TODO dest_quat_vel

        self.dest_quat_predict = quaternion.slerp_evaluate(
            self.prev_dest_quat, self.dest_quat, 1.0)

    def _set_velocity_setpoints(self):
        phi_vel, th_vel = self._get_next_velocity()
        self.motor_phi.set_velocity_setpoint(phi_vel)
        self.motor_th .set_velocity_setpoint(th_vel)

    def _update_quats(self):
        self.prev_quat = self.curr_quat
        self.curr_quat = rot_quat_to_pos_quat(self.curr_rot)
        self.prev_dest_quat = self.dest_quat
        self.dest_quat = self.coordinate_generator.dest_quat
