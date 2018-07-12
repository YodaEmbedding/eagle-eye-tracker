import numpy as np
import quaternion

from .coordinatemath import (apply_rotation, pos_quats_to_plot_coords)
from .testpaths import test_paths
from .path import Path

# TODO modify actual coordinate generator to send betwen [0,1] [0,1] for x, y
class CoordinateGenerator:
    """Generates coordinates to simulate a moving object."""

    def __init__(self):
        # self.coord = (0.0, 1.0)  # TODO deal with case where we overshoot pole
        self.coord = (0.0, 0.0)
        self.width  = 0.4
        self.height = 0.3

        self.path = test_paths[0]

    def draw(self, ax):
        """Draw a coordinate at location in image frame."""
        ax.scatter3D(*pos_quats_to_plot_coords([self._draw_quat]),
            s=50, color="#ff55bb")

    def update(self, dt, rot):
        """Updates generated coordinate.

        Args:
            dt (float): Time elapsed since last update() call.
            rot (float): Rotation quaternion to same frame as camera.
        """
        self._update_coord(dt, rot)
        v = self._get_offset_quat()
        self._draw_quat = apply_rotation(v, rot)
        self.dest_quat = self._draw_quat / np.abs(self._draw_quat)

    def _get_offset_quat(self):
        """Get position quaternion to express offset from (1,0,0) axis."""
        return np.quaternion(0., 1.,
            -self.width  * self.coord[0],
             self.height * self.coord[1])

    def _update_coord(self, dt, rot):
        v = self.path.get_next_pos_quat(dt)
        offset = apply_rotation(v, rot.inverse())
        coord = np.clip([
            -offset.y / self.width,
             offset.z / self.height], -1., 1.)
        self.coord = tuple(coord)

