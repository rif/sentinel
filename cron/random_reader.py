import random

class RandomReader(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def read(self):
        info_array = []
        for i in range(7):
            info_array.append(random.randint(0,100))
        return info_array
