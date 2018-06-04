#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
import quaternion

from matplotlib.animation import FuncAnimation
from mpl_toolkits import mplot3d

np.set_printoptions(precision=3)

# TODO make use of these classes so that we don't get weird sign issues
# EDIT: Nevermind, I got rid of sign issues by changing convention for Euler angles
class XY:
    __slots__ = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Does this really make any sense?
    # This is not truly a correspondence between the two coordinate systems.
    def to_euler(self):
        return Euler(self.x, self.y)

class Euler:
    __slots__ = ['phi', 'th']

    def __init__(self, phi, th):
        self.phi = phi
        self.th  = th

    # Does this really make any sense?
    # This is not truly a correspondence between the two coordinate systems.
    def to_xy(self):
        return (self.phi, self.th)

# Maybe a more apt conversion is from xy to "quaternion" coming out from x axis

class CoordinateGenerator:
    def __init__(self):
        self.coord = (0.2, 0.2)
        self.width  = 0.4
        self.height = 0.3

    def draw(self, ax, rot):
        v = self.get_offset_quat()
        v_ = apply_rotation(v, rot)
        ax.scatter3D(*quats_to_plot_coords([v_]), color="#ff55bb")

    def get_offset_quat(self):
        return np.quaternion(0., 1.,
            -self.width  * self.coord[0],
             self.height * self.coord[1])

    def get_next_coordinate(self, dt):
        return self.coord

class MotionController:
    def __init__(self):
        self.coordinate_generator = CoordinateGenerator()

        # Current position in Euler angles
        # Consider storing current position as a quaternion as well...?
        self.phi = 0.0
        self.th  = 0.0

        self.phi_pwr = 1.0
        self.th_pwr  = 0.0

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

    def set_motor_power(self, phi_pwr, th_pwr):
        self.phi_pwr = phi_pwr
        self.th_pwr  = th_pwr

    # TODO time delays, inertia, etc?
    def update(self, dt):
        coord = self.coordinate_generator.get_next_coordinate(dt)

        # TODO change this to depend on quaternion?
        self.phi_pwr = coord[0]
        self.th_pwr  = coord[1]

        self.phi += self.phi_pwr * dt
        self.th  += self.th_pwr  * dt
        self.rot = get_euler_rotation_quat(self.phi, self.th)

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
# Motor class: Velocity curves (with peak velocity), impedances
# ControlSystem class
# Latency
# Document sign, axis conventions
# machine learn control hyperparameters (differentiable programming or genetic)
# bounds of motion
# reversal of orientation
# consider latency from camera->imageproc->coords too
# renormalize after rotations? (prevents drift from surface of sphere)
# switch to plot.ly, Mayavi2, etc?

