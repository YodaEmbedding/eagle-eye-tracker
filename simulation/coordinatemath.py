import numpy as np
import quaternion

class Euler:
    __slots__ = ['phi', 'th']

    def __init__(self, phi, th):
        self.phi = phi
        self.th  = th

class XY:
    __slots__ = ['x', 'y']

    def __init__(self, x, y):
        self.x = x
        self.y = y

def apply_rotation(v, rot):
    return rot * v * rot.inverse()

def axis_angle_to_quat(axis, angle):
    """Get rotation quaternion from axis and angle of rotation.

    Takes in axis and angle and applies the formula:

    [cos(a/2), sin(a/2)*x, sin(a/2)*y, sin(a/2)*z]

    Args:
        axis (np.ndarray): Axis of rotation. Please ensure it is of unit norm.
        angle (float): Angle of rotation.

    Returns:
        np.quaternion: Unit quaternion describing rotation.
    """
    th = 0.5 * angle
    q = np.concatenate(([np.cos(th)], np.sin(th) * axis))
    return quaternion.as_quat_array(q)

def euler_to_pos_quat(phi, th):
    """Convert Euler angles to position quaternion.

    By project convention, the Euler angles are a composition of
    a rotation about the original x axis (roll),
    a rotation about the original y axis (pitch), and
    a rotation about the original z axis (yaw).
    This is also known as x-y-z, consisting of extrinsic rotations.

    Args:
        phi (float): First rotation about y axis (pitch).
        th (float): Second rotation about unrotated z axis (yaw).

    Returns:
        np.quaternion: Position quaterion.
    """
    return rot_quat_to_pos_quat(euler_to_rot_quat(phi, th))

def euler_to_rot_quat(phi, th):
    """Convert Euler angles to rotation quaternion.

    By project convention, the Euler angles are a composition of
    a rotation about the original x axis (roll),
    a rotation about the original y axis (pitch), and
    a rotation about the original z axis (yaw).
    This is also known as x-y-z, consisting of extrinsic rotations.

    Args:
        phi (float): First rotation about y axis (pitch).
        th (float): Second rotation about unrotated z axis (yaw).

    Returns:
        np.quaternion: Rotation quaterion.
    """
    return quaternion.from_spherical_coords(th, phi)
    # th_axis  = np.array([0., 1., 0.])
    # phi_axis = np.array([0., 0., 1.])
    # th_quat  = axis_angle_to_quat(th_axis,  th)
    # phi_quat = axis_angle_to_quat(phi_axis, phi)
    # return phi_quat * th_quat

def extrapolate_quat(q1, q2, t):
    rot = q2 * q1.inverse()
    return rot**t * q1

# TODO write unit test converting to/from euler and check if it's identity
def pos_quat_to_euler(q):
    """Convert position quaternion to Euler angles.

    A position quaternion is of form (0, x, y, z).

    By project convention, the Euler angles are a composition of
    a rotation about the original x axis (roll),
    a rotation about the original y axis (pitch), and
    a rotation about the original z axis (yaw).
    This is also known as x-y-z, consisting of extrinsic rotations.

    Args:
        q (np.quaternion): Position quaternion.

    Returns:
        np.ndarray: Euler angles in project convention.
    """

    # x =  r * cos(th) * cos(phi)
    # y =  r * cos(th) * sin(phi)
    # z = -r * sin(th)

    r   =  np.abs(q)
    th  = -np.arcsin(q.z / r)
    phi =  np.arctan2(q.y, q.x)

    return np.array([phi, th])

def pos_quats_to_plot_coords(q):
    arr = quaternion.as_float_array(q)
    return tuple(arr.T[1:])

def pos_quat_to_rot_quat(q):
    return euler_to_rot_quat(*pos_quat_to_euler(q))

def rot_quat_to_euler(q):
    """Convert rotation quaternion to Euler angles.

    A rotation quaternion is applied to position quaternions to compute
    rotations. This function accepts

    By project convention, the Euler angles are a composition of
    a rotation about the original x axis (roll),
    a rotation about the original y axis (pitch), and
    a rotation about the original z axis (yaw).
    This is also known as x-y-z, consisting of extrinsic rotations.

    Args:
        q (np.quaternion): Rotation quaternion.

    Returns:
        np.ndarray: Euler angles in project convention.
    """
    return tuple(reversed(q.as_spherical_coords()))

    # # yzy
    # # (phi, th, idk)
    # euler = np.empty(q.shape + (3,), dtype=np.float)
    # n = np.norm(q)
    # q = quaternion.as_float_array(q)
    # euler[..., 0] = (
    #     np.arctan2( q[..., 2], q[..., 0]) -
    #     np.arctan2(-q[..., 1], q[..., 3]))
    # euler[..., 1] = 2 * np.arccos(np.sqrt((q[..., 0]**2 + q[..., 2]**2) / n))
    # euler[..., 2] = (
    #     np.arctan2( q[..., 2], q[..., 0]) +
    #     np.arctan2(-q[..., 1], q[..., 3]))
    # return euler

    # w = q.w
    # x = q.x
    # y = q.y
    # z = q.z

    # ysqr = y * y
    #
    # t0 = +2.0 * (w * x + y * z)
    # t1 = +1.0 - 2.0 * (x * x + ysqr)
    # X = math.atan2(t0, t1)
    #
    # t2 = +2.0 * (w * y - z * x)
    # t2 = +1.0 if t2 > +1.0 else t2
    # t2 = -1.0 if t2 < -1.0 else t2
    # Y = math.asin(t2)
    #
    # t3 = +2.0 * (w * z + x * y)
    # t4 = +1.0 - 2.0 * (ysqr + z * z)
    # Z = math.atan2(t3, t4)
    #
    # return np.degrees(np.array([X, Y, Z]))

    # Also consider implementation from:
    # https://stackoverflow.com/a/27497022/365102

def rot_quat_to_pos_quat(q):
    return apply_rotation(quaternion.x, q)

def shortest_deg(src, dest):
    """Find shortest signed angle between dest and src."""
    return (dest - src + 180) % 360 - 180

def shortest_rad(src, dest):
    """Find shortest signed angle between dest and src."""
    return (dest - src + np.pi) % (2 * np.pi) - np.pi

