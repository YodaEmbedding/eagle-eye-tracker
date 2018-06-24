import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest

from simulation.worldstate import WorldState

np.set_printoptions(precision=3)
plt.style.use('dark_background')

def test_worldstate():
    state = WorldState()
    for _ in range(state.error_history.shape[0]):
        state.update()

    fig, ax = plt.subplots()
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)
    state.draw_error(ax)
    fig.savefig('test.png')

    mean = np.mean(state.error_history)
    std = np.std(state.error_history)

    print(mean, std)
    assert mean < 0.4 and std < 0.3

