#!/bin/env python
random_reader = local_import('random_reader')
ssh_reader = local_import('ssh_reader')
#snmp_reader = local_import('snmp_reader')

class_dict = {'rnd': random_reader.RandomReader,
              'ssh': ssh_reader.SSHReader,
              'snmp': random_reader.RandomReader}

for s in db(db.server.is_active == True).select():
    try:
        reader = class_dict[s.reader](s.address, s.port)
        info_array = reader.read()
        db.reading.insert(server=s.id,
                          cpu_utilization = info_array[0],
                          mem_total = info_array[1],
                          mem_used = info_array[2],
                          swap_total = info_array[3],
                          swap_used = info_array[4],
                          )
    except: pass
db.commit()

    