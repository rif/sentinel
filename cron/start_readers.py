#!/bin/env python
from random_reader import RandomReader

class_dict = {'rnd': RandomReader,
              'ssh': RandomReader,
              'snmp': RandomReader}

for s in db(db.server.is_active == True).select():
    reader = class_dict[s.reader](s.address, s.port)
    info_array = reader.read()
    db.reading.insert(server=s.id,
                      cpu_utilization = info_array[0],
                      mem_total = info_array[1],
                      mem_used = info_array[2],
                      mem_utilization = info_array[3],
                      swap_total = info_array[4],
                      swap_used = info_array[5],
                      swap_utilization = info_array[6]
                      )
    db.commit()

    
