#!/usr/bin/env python3

from functools import partial

import matplotlib.pyplot as plt
import numpy as np
import quaternion

from matplotlib.animation import FuncAnimation
from mpl_toolkits import mplot3d

np.set_printoptions(precision=3)

class WorldState:
    def __init__(self):
        # Current position in Euler angles
        # Consider storing current position as a quaternion as well...?
        self.phi = 0.0
        self.th  = 0.0

    def draw(self, frame_number, ax):
        self.phi += 1 / 16 * np.pi
        square2 = apply_euler_rotation(square, self.phi, self.th)

        phi = 0 / 16 * np.pi
        th  = -frame_number / 16 * np.pi
        square3 = apply_euler_rotation(square, phi, th)

        origin = np.zeros((1, 3))

        ax.clear()
        ax.scatter3D(*tuple(origin.T), color="red")
        draw_sphere(ax, 8, 16, color="#cccccc")
        ax.plot3D(*quats_to_plot_coords(square),  color='#bb55ff')
        ax.plot3D(*quats_to_plot_coords(square2), color='#ffbb55')
        ax.plot3D(*quats_to_plot_coords(square3), color='#55bbff')

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

w = 0.5
h = 0.3
square = np.array([
    np.quaternion(0, 1,  w,  h),  # A
    np.quaternion(0, 1, -w,  h),  # B
    np.quaternion(0, 1, -w, -h),  # C
    np.quaternion(0, 1,  w, -h),  # D
    np.quaternion(0, 1,  w,  h),  # A
    np.quaternion(0, 1, -w, -h),  # C
    np.quaternion(0, 1, -w,  h),  # B
    np.quaternion(0, 1,  w, -h),  # D
])

fig = plt.figure()
ax = plt.axes(projection='3d')
ax.set_aspect('equal')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_zlabel('z')
ax.view_init(elev=0., azim=0.)

state = WorldState()

update = partial(state.draw, ax=ax)
animation = FuncAnimation(fig, update, 65536, interval=50, blit=False)

plt.show()

# TODO
# construct point follower (follows a point it sees on "camera")
# construct model with motors (with velocity curves; max velocity), impedances, latency
# machine learn control hyperparameters (differentiable programming or genetic)
# consider latency from camera->imageproc->coords too
# switch to plot.ly, Mayavi2, etc?

