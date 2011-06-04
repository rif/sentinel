#!/bin/env python
from random_reader import RandomReader
from ssh_reader import SSHReader
snmp_reader = local_import('snmp_reader')

class_dict = {'rnd': RandomReader,
              'ssh': SSHReader,
              'snmp': snmp_reader.SNMPReader}

for s in db(db.server.is_active == True).select():
    try:
        reader = class_dict[s.reader](s.address, s.port)
        info_array = reader.read()
        db.reading.insert(server = s.id, cpu_utilization = info_array[0], mem_total = info_array[1], mem_used = info_array[2], swap_total = info_array[3], swap_used = info_array[4])
    except:
        db.reading.insert(server = s.id, cpu_utilization = -1, mem_total = -1, mem_used = -1, swap_total = -1, swap_used = -1)
        
db.commit()

    
