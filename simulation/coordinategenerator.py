import numpy as np
import quaternion

from coordinatemath import (apply_rotation, euler_to_pos_quat,
    pos_quats_to_plot_coords)

# TODO modify actual coordinate generator to send betwen [0,1] [0,1] for x, y
class CoordinateGenerator:
    """Generates coordinates to simulate a moving object."""

    def __init__(self):
        # self.coord = (0.0, 1.0)  # TODO deal with case where we overshoot pole
        self.coord = (0.0, 0.0)
        self.width  = 0.4
        self.height = 0.3

        self.path = Path(np.array([
            #  t,  phi,   th
            [0.0,  0.0,  0.0],
            [1.0,  0.5, -0.5],
            [2.0,  1.0, -1.0],
            [3.0,  1.0, -1.5],
            [4.0,  2.0, -1.5],
            [5.0,  5.0, -1.3],
            [6.0,  7.0, -1.2],
            [7.0,  6.0, -1.1],
            [8.0, -1.0, -1.0],
            [9.0,  0.0, -0.3],
        ]))

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

class Path:
    """Defines a path through time and space."""

    def __init__(self, path):
        self.path = path
        self.t = 0.0

    # TODO consider SLERP, or other smooth quat interp methods
    # Smooth paths on Reimannian manifolds... homotopies? Geodesics?
    # Oh my gosh
    def get_next_pos_quat(self, dt):
        self.t += dt
        phi, th = self._get_curr_euler()
        return euler_to_pos_quat(phi, th)

    def _get_curr_euler(self):
        """Returns a (phi, th) vector for the given time."""

        n_rows = self.path.shape[0]
        idx = np.searchsorted(self.path[:, 0], self.t, side='right')

        if idx >= n_rows:
            self.t = -5.0
            idx = 0

        l = self.path[idx - 1]
        r = self.path[idx]

        p_l = l[1:]
        p_r = r[1:]

        t_l = l[0]
        t_r = r[0]
        t = (self.t - t_l) / (t_r - t_l)

        # TODO what about wrapping of angles? around branches
        # using euler angles is a terribad idea
        return (p_r - p_l) * t + p_l

