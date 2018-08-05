#!/usr/bin/env python3

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.animation import FuncAnimation
from mpl_toolkits import mplot3d

from tracker.worldstate import WorldState

np.set_printoptions(precision=3)
mpl.rcParams['toolbar'] = 'None'
plt.style.use('dark_background')

scale = 5
fig = plt.figure(figsize=(2.0 * scale, 1 * scale), dpi=100)
fig.set_facecolor('#111111')
fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)

axes = []
axes.append(fig.add_subplot(1, 2, 1))
axes.append(fig.add_subplot(1, 2, 2, projection='3d'))
ax_error = axes[0]
ax_3d    = axes[1]

ax_3d.set_aspect('equal')
ax_3d.view_init(elev=0., azim=0.)
# ax_3d.view_init(elev=90., azim=0.)

state = WorldState()

def update(frame_number):
    state.update()
    state.draw_3d(ax_3d)
    state.draw_error(ax_error)

ani = FuncAnimation(fig, update, 65536, interval=50, blit=False)

# ani.save('animation.mp4', fps=20, dpi=100)
plt.show()

# TODO
# Document sign, axis conventions
# PID controller
# Pathing
# Motor class: impedances/velocity-accel ramp curves
# Model time delay/latency, inertia
# machine learn control hyperparameters (differentiable programming or genetic)
# bounds of motion
# Model inertia of camera mass (not just motors)
# renormalize after rotations? (prevents drift from surface of sphere)
# switch to plot.ly, Mayavi2, etc?
