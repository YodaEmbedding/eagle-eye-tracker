import numpy as np
from numpy_ringbuffer import RingBuffer

from .coordinategenerator import CoordinateGenerator, LatentCoordinateGenerator
from .drawutils import draw_sphere, set_axes_radius
from .motioncontroller import MotionController
from .motor import Motor
from .virtualmotor import VirtualMotor

class WorldState:
    """Keeps track of all simulated worldy elements."""

    def __init__(self):
        self.coord_gen = CoordinateGenerator()
        self.latent_coord_gen = LatentCoordinateGenerator(self.coord_gen)

        # Stepper.STEPS_PER_REV = 51200
        motor_phi = Motor(VirtualMotor(accel_max=1.96, velocity_max=0.49),
            bound_min=-np.inf, bound_max=np.inf)
        motor_th  = Motor(VirtualMotor(accel_max=1.96, velocity_max=0.49),
            bound_min=-0.5*np.pi, bound_max=0.0)

        self.motion_controller = MotionController(self.latent_coord_gen,
            motor_phi, motor_th)

        capacity = 512
        self.error_history = RingBuffer(capacity=capacity, dtype=np.float32)
        self.error_history_latent = RingBuffer(capacity=capacity,
            dtype=np.float32)
        self.error_history.extend(np.zeros(capacity))
        self.error_history_latent.extend(np.zeros(capacity))

    def draw_3d(self, ax):
        origin = np.zeros((1, 3))

        ax.clear()
        ax.scatter3D(*tuple(origin.T), color="red")
        draw_sphere(ax, 8, 16, color="#222222")
        self.motion_controller.draw(ax)

        ax.margins(x=0, y=0)
        ax.axis('off')
        ax.grid(False)
        # ax.set_title('Simulation')
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_zlabel('z')
        set_axes_radius(ax, origin[0], 0.7)

    def draw_error(self, ax):
        x = np.arange(len(self.error_history))
        y = np.array(self.error_history)

        x_l = np.arange(len(self.error_history_latent))
        y_l = np.array(self.error_history_latent)

        ax.clear()
        ax.plot(x,   y,   color="#ff55bb")
        ax.plot(x_l, y_l, color="#772255")
        ax.axis('off')
        ax.grid(False)
        ax.set_title('Error', position=(0.5, 0.9))
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_ylim([0, 1.42])

    def update(self, dt):
        self.motion_controller.update(dt)
        error   = np.linalg.norm(self.coord_gen.coord)
        error_l = np.linalg.norm(self.latent_coord_gen.coord)
        self.error_history.append(error)
        self.error_history_latent.append(error_l)
