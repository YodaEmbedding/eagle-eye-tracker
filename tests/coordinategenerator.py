import numpy as np
import quaternion

from coordinatemath import apply_rotation, quats_to_plot_coords

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
