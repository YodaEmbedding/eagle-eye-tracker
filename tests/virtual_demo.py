#!/usr/bin/env python3

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
        self.velocity_max = 3.0

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
        self.coord = (1.0, 0.05)
        self.width  = 0.4
        self.height = 0.3

    def draw(self, ax, rot):
        v = self._get_offset_quat()
        v_ = apply_rotation(v, rot)
        ax.scatter3D(*quats_to_plot_coords([v_]), color="#ff55bb")

    def get_next_coordinate(self, dt):
        return self.coord

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
        self.coordinate_generator.draw(ax, self.rot)

    # TODO time delays, inertia, etc?
    def update(self, dt):
        coord = self.coordinate_generator.get_next_coordinate(dt)

        # TODO change this to depend on quaternion?
        phi_pwr = 10000 * coord[0]
        th_pwr  = 10000 * coord[1]

        self.motor_phi.set_velocity_setpoint(phi_pwr)
        self.motor_th .set_velocity_setpoint(th_pwr)

        self.motor_phi.update(dt)
        self.motor_th .update(dt)

        self.rot = get_euler_rotation_quat(
            self.motor_phi.position,
            self.motor_th.position)

        self.rect_drawable = apply_rotation(self._rect_drawable_orig, self.rot)

class WorldState:
    def __init__(self):
        self.motion_controller = MotionController()

    def draw(self, ax):
        origin = np.zeros((1, 3))

        ax.clear()
        ax.scatter3D(*tuple(origin.T), color="red")
        draw_sphere(ax, 8, 16, color="#cccccc")
        self.motion_controller.draw(ax)

        plt.axis('off')
        ax.grid(False)
        set_axes_radius(ax, origin[0], 1)

    def update(self):
        dt = 50 / 1000
        self.motion_controller.update(dt)

def apply_rotation(v, rot):
    return rot * v * rot.inverse()

def get_euler_rotation_quat(phi, th):
    th_axis  = np.array([0., 1., 0.])
    phi_axis = np.array([0., 0., 1.])
    th_quat  = get_rotation_quat(th_axis,  -th)
    phi_quat = get_rotation_quat(phi_axis, -phi)
    return phi_quat * th_quat

def get_rotation_quat(axis, angle):
    """[cos(a/2), sin(a/2)*x, sin(a/2)*y, sin(a/2)*z]"""
    th = 0.5 * angle
    q = np.concatenate(([np.cos(th)], np.sin(th) * axis))
    return quaternion.as_quat_array(q)

def quats_to_plot_coords(q):
    arr = quaternion.as_float_array(q)
    return tuple(arr.T[1:])

def draw_sphere(ax, latitudes, longitudes, color):
    latitudes  = (latitudes  + 1) * 1j
    longitudes = (longitudes + 1) * 1j
    u, v = np.mgrid[0:2*np.pi:longitudes, 0:np.pi:latitudes]
    x = np.cos(u) * np.sin(v)
    y = np.sin(u) * np.sin(v)
    z = np.cos(v)
    ax.plot_wireframe(x, y, z, color=color)

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
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
ax.view_init(elev=0., azim=0.)

state = WorldState()

def update(frame_number):
    state.update()
    state.draw(ax)

animation = FuncAnimation(fig, update, 65536, interval=50, blit=False)

plt.show()

# TODO
# Motor class: Velocity curves (with peak velocity), impedances
# ControlSystem class
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

