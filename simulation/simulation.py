#!/usr/bin/env python3

import numpy as np

from worldstate import WorldState
import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation
from mpl_toolkits import mplot3d

np.set_printoptions(precision=3)

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

