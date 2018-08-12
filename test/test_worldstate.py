import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest

from tracker.coordinategenerator import LatentCoordinateGenerator
from tracker.worldstate import WorldState

np.set_printoptions(precision=3)
plt.style.use('dark_background')

# TODO use same boilerplate but for different paths to test different paths
# and characteristics such as oscillatory behavior
def test_worldstate():
    dt = 50 / 1000
    latency = LatentCoordinateGenerator.COORD_LATENCY
    state = WorldState()
    for _ in range(state.error_history.shape[0]):
        state.update(dt)

    hist = state.error_history
    hist_max  = np.max(hist)
    hist_mean = np.mean(hist)
    hist_std  = np.std(hist)

    fig, ax = plt.subplots()
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)
    state.draw_error(ax)
    fig.savefig('log/test_worldstate_{:.3f}_{:.3f}_{:.3f}_{:.3f}.png'.format(
        latency, hist_max, hist_mean, hist_std))

    # assert hist_max  < 0.9
    # assert hist_mean < 0.4
    # assert hist_std  < 0.3

