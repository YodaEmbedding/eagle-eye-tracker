#!/usr/bin/env python3

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
import quaternion

from matplotlib.animation import FuncAnimation
from mpl_toolkits import mplot3d

np.set_printoptions(precision=3)

class CoordinateGenerator:
    def __init__(self):
        self.coordinate = (0.1, 0.1)

    def get_next_coordinate(dt):
        return self.coordinate

class MotionController:
    def __init__(self):
        # Current position in Euler angles
        # Consider storing current position as a quaternion as well...?
        self.phi = 0.0
        self.th  = 0.0

        self.phi_pwr = 1.0
        self.th_pwr  = 0.0

    # TODO time delays, inertia, etc?
    def update(self, dt):
        self.phi += self.phi_pwr * dt
        self.th  += self.th_pwr  * dt

    def set_motor_power(self, phi_pwr, th_pwr):
        self.phi_pwr = phi_pwr
        self.th_pwr  = th_pwr

class WorldState:
    def __init__(self):
        self.motion_controller = MotionController()

        # TODO isn't it strange that this class is managing squares?
        w = 0.4
        h = 0.3
        self._square_orig = np.array([
            np.quaternion(0, 1,  w,  h),  # A
            np.quaternion(0, 1, -w,  h),  # B
            np.quaternion(0, 1, -w, -h),  # C
            np.quaternion(0, 1,  w, -h),  # D
            np.quaternion(0, 1,  w,  h),  # A
            np.quaternion(0, 1, -w, -h),  # C
            np.quaternion(0, 1, -w,  h),  # B
            np.quaternion(0, 1,  w, -h),  # D
        ])

    def update(self):
        dt = 50 / 1000
        self.motion_controller.update(dt)
        self.square = apply_euler_rotation(
            self._square_orig,
            self.motion_controller.phi,
            self.motion_controller.th)

    def draw(self, ax):
        origin = np.zeros((1, 3))

        ax.clear()
        ax.scatter3D(*tuple(origin.T), color="red")
        draw_sphere(ax, 8, 16, color="#cccccc")
        ax.plot3D(*quats_to_plot_coords(self.square), color='#55bbff')

        plt.axis('off')
        ax.grid(False)
        set_axes_radius(ax, origin[0], 1)

def get_rotation_quaternion(axis, angle):
    """[cos(a/2), sin(a/2)*x, sin(a/2)*y, sin(a/2)*z]"""
    th = 0.5 * angle
    q = np.concatenate(([np.cos(th)], np.sin(th) * axis))
    return quaternion.as_quat_array(q)

def apply_rotation(v, axis, angle):
    R = get_rotation_quaternion(axis, angle)
    return R * v * R.inverse()

def apply_euler_rotation(v, phi, th):
    th_axis  = np.array([0., 1., 0.])
    phi_axis = np.array([0., 0., 1.])

    v_ = v
    v_ = apply_rotation(v_, th_axis,  th)
    v_ = apply_rotation(v_, phi_axis, phi)

    return v_

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

def set_axes_equal(ax):
    '''Make axes of 3D plot have equal scale so that spheres appear as spheres,
    cubes as cubes, etc..  This is one possible solution to Matplotlib's
    ax.set_aspect('equal') and ax.axis('equal') not working for 3D.

    Input
      ax: a matplotlib axis, e.g., as output from plt.gca().
    '''

    limits = np.array([
        ax.get_xlim3d(),
        ax.get_ylim3d(),
        ax.get_zlim3d(),
    ])

    origin = np.mean(limits, axis=1)
    radius = 0.5 * np.max(np.abs(limits[:, 1] - limits[:, 0]))
    set_axes_radius(ax, origin, radius)

fig = plt.figure()
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
# construct point follower (follows a point it sees on "camera")
# Motioncontroller/Robot class? (Maintains phi, th, moves motors at given velocities)
# Tracker class? (Finds best path for robot... or maybe put this in robot)
# ImgProc simulator (e.g. always on top right of square for now...)

# construct model with motors (with velocity curves; max velocity), impedances, latency
# machine learn control hyperparameters (differentiable programming or genetic)
# consider latency from camera->imageproc->coords too
# switch to plot.ly, Mayavi2, etc?
# renormalize after rotations? (prevents drift from surface of sphere)

