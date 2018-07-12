import numpy as np
import quaternion

from .coordinatemath import euler_to_pos_quat

class Path:
    """Defines a path through time and space."""

    def __init__(self, path):
        self.path = path
        self.path_quat = np.array([euler_to_pos_quat(*p) for p in path[:, 1:]])
        self.path_t    = path[:, 0]
        self.t = 0.0

    def get_next_pos_quat(self, dt):
        self.t += dt
        # print('CoordinateGenerator t: {:.2f}'.format(self.t))
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

