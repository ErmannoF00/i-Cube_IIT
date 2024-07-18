import time


class Timer:

    def __init__(self):
        self.t_start = time.time()
        self.t_currn = time.time()
        pass

    def initialise(self):
        self.t_start = time.time()

    def update(self):
        self.t_currn = time.time()

    def elapsed(self):
        return time.time() - self.t_start