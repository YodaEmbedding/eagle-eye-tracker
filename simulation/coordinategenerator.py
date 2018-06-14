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

        test_paths = [
            Path(np.array([
                #  t,  phi,   th
                [0.0,  0.0,  0.0],
                [1.0,  0.5, -0.2],
                [2.0,  1.0, -0.5],
                [3.0,  1.0, -0.7],
                [4.0,  2.0, -0.8],
                [5.0,  3.0, -0.6],
                [6.0,  4.0, -0.4],
                [7.0,  5.0, -0.2],
                [8.0, -1.0, -0.1],
                [9.0,  0.0,  0.0],
                #  t,  phi,   th
                [10.0,  0.0,  0.0],
                [11.0,  0.0,  0.0],
                [12.0,  0.5, -0.2],
                [13.0,  0.5, -0.2],
                [14.0,  0.0,  0.0],
                [15.0,  0.0,  0.0],
                [16.0,  0.5, -0.2],
                [17.0,  0.5, -0.2],
                [18.0,  0.0,  0.0],
                [19.0,  0.0,  0.0]])),
            Path(np.array([
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
                [9.0,  0.0, -0.3]])),
        ]

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

class Path:
    """Defines a path through time and space."""

    def __init__(self, path):
        self.path = path
        self.path_quat = np.array([euler_to_pos_quat(*p) for p in path[:, 1:]])
        self.path_t    = path[:, 0]
        self.t = 0.0

    def get_next_pos_quat(self, dt):
        self.t += dt
        print('CoordinateGenerator t: {:.2f}'.format(self.t))
        return self.pos_quat

    @property
    def pos_quat(self):
        n_rows = self.path.shape[0]
        idx = max(self.path_t.searchsorted(self.t, side='right'), 1)

        if idx >= n_rows:
            self.t = -1.
            idx = 1

        q_l = self.path_quat[idx - 1]
        q_r = self.path_quat[idx]

        t_l = self.path_t[idx - 1]
        t_r = self.path_t[idx]
        t = (max(self.t, 0.) - t_l) / (t_r - t_l)

        return quaternion.squad(
            self.path_quat,
            self.path_t,
            np.array([max(self.t, 0.)]))[0]

