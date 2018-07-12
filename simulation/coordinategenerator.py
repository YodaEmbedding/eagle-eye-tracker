import numpy as np
import quaternion

from .coordinatemath import (apply_rotation, pos_quats_to_plot_coords)
from .testpaths import test_paths

# TODO modify actual coordinate generator to send between [-1,1] [-1,1] for x, y
# ensure proper aspect ratio that we expect
class CoordinateGenerator:
    """Generates coordinates to simulate a moving object."""

    def __init__(self, coord_getter_func=None):
        self.coord_getter_func = coord_getter_func

        self.coord = (0.0, 0.0)

        # TODO measure
        self.width  = 0.4
        self.height = 0.3

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
        """Calculates next coord from coord_getter_func or path."""
        if self.coord_getter_func is not None:
            self.coord = self.coord_getter_func()
            return

        v = test_paths[0].get_next_pos_quat(dt)
        offset = apply_rotation(v, rot.inverse())
        coord = np.clip([
            -offset.y / self.width,
             offset.z / self.height], -1., 1.)
        self.coord = tuple(coord)

