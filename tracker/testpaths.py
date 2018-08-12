import numpy as np

from .path import Path

test_paths = [
    Path(np.array([
        #  t,  phi,   th
        [0.0,   0.0,  0.0],
        [2.0,   0.5, -0.2],
        [4.0,   1.0, -0.5],
        [6.0,   1.0, -0.7],
        [8.0,   2.0, -0.8],
        [10.0,  3.0, -0.6],
        [12.0,  4.0, -0.4],
        [14.0,  5.0, -0.2],
        [16.0, -1.0, -0.1],
        [18.0,  0.0,  0.0],
        #  t,  phi,   th
        [20.0,  0.0,  0.0],
        [22.0,  0.0,  0.0],
        [24.0,  0.5, -0.2],
        [26.0,  0.5, -0.2],
        [28.0,  0.0,  0.0],
        [30.0,  0.0,  0.0],
        [32.0,  0.5, -0.2],
        [34.0,  0.5, -0.2],
        [36.0,  0.0,  0.0],
        [38.0,  0.0,  0.0]])),
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
