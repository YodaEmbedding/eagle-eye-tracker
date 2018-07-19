# TODO insert process too? or is that stupid
class CommComm:
    def __init__(self):
        self.queue_in  = Queue()
        self.queue_out = Queue()

        self.latest_msg = None
        self.latest_coord = (0, 0)

    def get_args(self):
        return self.queue_out, self.queue_in

    def run(self):
        # TODO this is stupid
        # Clear queue
        while not self.queue_in.empty():
            self.latest_msg = self.queue_in.get()
            self._parse_msg()  # TODO shouldn't this just be part of a setter

    def update(self, dt):
        pass

    def _parse_msg(self):
        m = re.match(r'\((\d+\.?\d*),(\d+\.?\d*)\)', self.latest_msg).groups()
        self.latest_coord = (float(m[0]), float(m[1]))

