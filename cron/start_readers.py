#!/bin/env python
from random_reader import RandomReader
from ssh_reader import SSHReader
from snmp_reader import SNMPReader

class_dict = {'rnd': RandomReader,
              'ssh': SSHReader,
              'snmp': SNMPReader}

for s in db(db.server.is_active == True).select():
    reader = class_dict[s.reader](s.address, s.port)
    info_array = reader.read()
    db.reading.insert(server=s.id,
                      cpu_utilization = info_array[0],
                      mem_total = info_array[1],
                      mem_used = info_array[2],
                      swap_total = info_array[3],
                      swap_used = info_array[4],
                      )
    db.commit()

    
