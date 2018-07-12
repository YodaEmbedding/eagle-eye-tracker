# TODO insert process too? or is that stupid
class StepperComm:
    def __init__(self, accel_max, velocity_max):
        self.queue_in  = Queue()
        self.queue_out = Queue()

        self.position = 0.0
        self.velocity = 0.0

        self.accel_max = accel_max
        self.velocity_max = velocity_max

    def get_args(self):
        return self.queue_out, self.queue_in

    def run(self):
        # TODO this is stupid
        # Clear queue
        while not self.queue_in.empty():
            self.position, self.velocity = self.queue_in.get()

    def set_velocity_setpoint(self, setpoint):
        self.queue_out.put(setpoint)
