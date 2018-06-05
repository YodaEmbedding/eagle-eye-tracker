#!/usr/bin/env python3

import math
import matplotlib.pyplot as plt
import numpy as np
import quaternion

from matplotlib.animation import FuncAnimation
from mpl_toolkits import mplot3d

np.set_printoptions(precision=3)

class XY:
    __slots__ = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y

class Euler:
    __slots__ = ['phi', 'th']

    def __init__(self, phi, th):
        self.phi = phi
        self.th  = th

# VirtualMotor... inherits from Motor?
class Motor:
    def __init__(self):
        self.position = 0.0
        self.velocity = 0.0
        self.velocity_setpoint = 0.0
        self.accel_max = 1.0
        self.velocity_max = 0.5

    def set_velocity_setpoint(self, velocity_setpoint):
        self.velocity_setpoint = velocity_setpoint

    def update(self, dt):
        dv = np.clip(self.velocity_setpoint - self.velocity,
            -self.accel_max * dt,
             self.accel_max * dt)
        self.velocity = np.clip(self.velocity + dv,
            -self.velocity_max, self.velocity_max)
        self.position += dt * self.velocity

class CoordinateGenerator:
    def __init__(self):
        # self.coord = (1.0, 0.05)
        self.coord = (1.0, 0.00)
        self.width  = 0.4
        self.height = 0.3

    def draw(self, ax):
        ax.scatter3D(*quats_to_plot_coords([self._draw_quat]),
            s=50, color="#ff55bb")

    def update(self, dt, rot):
        v = self._get_offset_quat()
        self._draw_quat = apply_rotation(v, rot)
        self.dest_quat = self._draw_quat / np.abs(self._draw_quat)

    def _get_offset_quat(self):
        return np.quaternion(0., 1.,
            -self.width  * self.coord[0],
             self.height * self.coord[1])

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

class WorldState:
    def __init__(self):
        self.motion_controller = MotionController()

    def draw(self, ax):
        origin = np.zeros((1, 3))

        ax.clear()
        ax.scatter3D(*tuple(origin.T), color="red")
        draw_sphere(ax, 8, 16, color="#222222")
        self.motion_controller.draw(ax)

        plt.axis('off')
        ax.grid(False)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        set_axes_radius(ax, origin[0], 0.7)

    def update(self):
        dt = 50 / 1000
        self.motion_controller.update(dt)

def apply_rotation(v, rot):
    return rot * v * rot.inverse()

def euler_to_quat(phi, th):
    """Convert Euler angles to unit quaternion.

    By project convention, the Euler angles are a composition of
    a rotation about the original x axis (roll),
    a rotation about the original y axis (pitch), and
    a rotation about the original z axis (yaw).
    This is also known as x-y-z, consisting of extrinsic rotations.

    Args:
        phi (float): First rotation about y axis (pitch).
        th (float): Second rotation about unrotated z axis (yaw).

    Returns:
        np.quaternion: Quaterion.
    """
    th_axis  = np.array([0., 1., 0.])
    phi_axis = np.array([0., 0., 1.])
    th_quat  = axis_angle_to_quat(th_axis,  -th)
    phi_quat = axis_angle_to_quat(phi_axis, -phi)
    return phi_quat * th_quat

def axis_angle_to_quat(axis, angle):
    """Get rotation quaternion from axis and angle of rotation.

    Takes in axis and angle and applies the formula:

    [cos(a/2), sin(a/2)*x, sin(a/2)*y, sin(a/2)*z]

    Args:
        axis (np.ndarray): Axis of rotation. Please ensure it is of unit norm.
        angle (float): Angle of rotation.

    Returns:
        np.quaternion: Unit quaternion describing rotation.
    """
    th = 0.5 * angle
    q = np.concatenate(([np.cos(th)], np.sin(th) * axis))
    return quaternion.as_quat_array(q)

# TODO write unit test converting to/from euler and check if it's identity
def quat_to_euler(q):
    """Convert unit quaternion to Euler angles.

    By project convention, the Euler angles are a composition of
    a rotation about the original x axis (roll),
    a rotation about the original y axis (pitch), and
    a rotation about the original z axis (yaw).
    This is also known as x-y-z, consisting of extrinsic rotations.

    Args:
        q (np.quaternion): Quaternion of unit norm.

    Returns:
        np.ndarray: Euler angles in project convention.
    """

    # # yzy
    # # (phi, th, idk)
    # euler = np.empty(q.shape + (3,), dtype=np.float)
    # n = np.norm(q)
    # q = quaternion.as_float_array(q)
    # euler[..., 0] = (
    #     np.arctan2( q[..., 2], q[..., 0]) -
    #     np.arctan2(-q[..., 1], q[..., 3]))
    # euler[..., 1] = 2 * np.arccos(np.sqrt((q[..., 0]**2 + q[..., 2]**2) / n))
    # euler[..., 2] = (
    #     np.arctan2( q[..., 2], q[..., 0]) +
    #     np.arctan2(-q[..., 1], q[..., 3]))
    # return euler

    w = q.w
    x = q.x
    y = q.y
    z = q.z

    # ysqr = y * y
    #
    # t0 = +2.0 * (w * x + y * z)
    # t1 = +1.0 - 2.0 * (x * x + ysqr)
    # X = math.atan2(t0, t1)
    #
    # t2 = +2.0 * (w * y - z * x)
    # t2 = +1.0 if t2 > +1.0 else t2
    # t2 = -1.0 if t2 < -1.0 else t2
    # Y = math.asin(t2)
    #
    # t3 = +2.0 * (w * z + x * y)
    # t4 = +1.0 - 2.0 * (ysqr + z * z)
    # Z = math.atan2(t3, t4)
    #
    # return np.degrees(np.array([X, Y, Z]))

    # maybe just convert x,y,z to phi, th directly...
    # x =  cos(th) * cos(phi)
    # y =  cos(th) * sin(phi)
    # z = -sin(th)

    th  = -np.arcsin(z)
    phi = np.arctan2(y, x)

    return np.array([phi, th])

def quats_to_plot_coords(q):
    arr = quaternion.as_float_array(q)
    return tuple(arr.T[1:])

def draw_sphere(ax, latitudes, longitudes, **kwargs):
    latitudes  = (latitudes  + 1) * 1j
    longitudes = (longitudes + 1) * 1j
    u, v = np.mgrid[0:2*np.pi:longitudes, 0:np.pi:latitudes]
    x = np.cos(u) * np.sin(v)
    y = np.sin(u) * np.sin(v)
    z = np.cos(v)
    ax.plot_wireframe(x, y, z, **kwargs)

def set_axes_radius(ax, origin, radius):
    ax.set_xlim3d([origin[0] - radius, origin[0] + radius])
    ax.set_ylim3d([origin[1] - radius, origin[1] + radius])
    ax.set_zlim3d([origin[2] - radius, origin[2] + radius])

plt.style.use('dark_background')
fig = plt.figure()
fig.set_facecolor('#111111')
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
ax = plt.axes(projection='3d')
ax.set_aspect('equal')
# ax.view_init(elev=0., azim=0.)
ax.view_init(elev=90., azim=0.)

state = WorldState()

def update(frame_number):
    state.update()
    state.draw(ax)

animation = FuncAnimation(fig, update, 65536, interval=50, blit=False)

plt.show()

# TODO
# Motor class: Velocity curves (with peak velocity), impedances
# ControlSystem class
# Pathing
# Latency
# Document sign, axis conventions
# machine learn control hyperparameters (differentiable programming or genetic)
# bounds of motion
# reversal of orientation
# Model inertia of camera mass (not just motors)
# consider latency from camera->imageproc->coords too
# renormalize after rotations? (prevents drift from surface of sphere)
# switch to plot.ly, Mayavi2, etc?
# Conversion from xy to "quaternion" coming out from x axis
# Graph error metric

