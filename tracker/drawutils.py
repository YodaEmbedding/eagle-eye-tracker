import numpy as np

def draw_sphere(ax, latitudes, longitudes, **kwargs):
    latitudes  = (latitudes  + 1) * 1j
    longitudes = (longitudes + 1) * 1j
    u, v = np.mgrid[0:2*np.pi:longitudes, 0:np.pi:latitudes]
    x = np.cos(u) * np.sin(v)
    y = np.sin(u) * np.sin(v)
    z = np.cos(v)
    ax.plot_wireframe(x, y, z, **kwargs)

def set_axes_radius(ax, origin, radius):
    ax.set_xlim3d([origin[0] - radius, origin[0] + radius])
    ax.set_ylim3d([origin[1] - radius, origin[1] + radius])
    ax.set_zlim3d([origin[2] - radius, origin[2] + radius])
