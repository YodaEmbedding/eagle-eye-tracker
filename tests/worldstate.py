import matplotlib.pyplot as plt
import numpy as np

from draw_utils import draw_sphere, set_axes_radius
from motioncontroller import MotionController

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

