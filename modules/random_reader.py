import random

class RandomReader(object):
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def read(self):
        info_array = []
        info_array.append(random.randint(1,100)) #cpu
        info_array.append(8000) #mem_total
        info_array.append(random.randint(0,8000)) #mem_used
        info_array.append(4000) #swap_total
        info_array.append(random.randint(0,8000)) #swap_used
        return info_array
