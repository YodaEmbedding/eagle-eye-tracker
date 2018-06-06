import numpy as np
import quaternion

from coordinatemath import apply_rotation, quats_to_plot_coords

class CoordinateGenerator:
    """Generates coordinates to simulate a moving object."""

    def __init__(self):
        # self.coord = (0.0, 1.0)  # TODO deal with case where we overshoot pole
        self.coord = (1.0, 0.1)
        self.width  = 0.4
        self.height = 0.3

        # TODO test modes other than just constant coordinate location...

    def draw(self, ax):
        """Draw a coordinate at location in image frame."""
        ax.scatter3D(*quats_to_plot_coords([self._draw_quat]),
            s=50, color="#ff55bb")

    def update(self, dt, rot):
        v = self._get_offset_quat()
        self._draw_quat = apply_rotation(v, rot)
        self.dest_quat = self._draw_quat / np.abs(self._draw_quat)

    def _get_offset_quat(self):
        """Get position quaternion to express offset from (1,0,0) axis."""
        return np.quaternion(0., 1.,
            -self.width  * self.coord[0],
             self.height * self.coord[1])
