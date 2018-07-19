# TODO insert process too? or is that stupid
class CommComm:
    def __init__(self):
        self.queue_in  = Queue()
        self.queue_out = Queue()

        self.latest_msg = None

    def get_args(self):
        return self.queue_out, self.queue_in

    def run(self):
        # TODO this is stupid
        # Clear queue
        while not self.queue_in.empty():
            self.latest_msg = self.queue_in.get()

    def update(self, dt):
        pass

