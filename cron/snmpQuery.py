from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.carrier.asynsock.dgram import udp
from pyasn1.codec.ber import encoder, decoder
from pysnmp.proto import api

from time import time, sleep
from datetime import timedelta

from iniParser import Parser

class SNMPQuery(object):
	def __init__(self, host, port=161):
		self.host = host
		self.port = port

		self.snmpTimeout = 10

		# Get all SNMP counters from config file
		snmpConfigParser = Parser()
		allCounters_dict = snmpConfigParser.getDictOfAllSectionsAndSettings()

		self.cpuSettings_dict = self.convertOIDToLocalOIDRepr(allCounters_dict['CPU_INFO'])
		self.memSettings_dict = self.convertOIDToLocalOIDRepr(allCounters_dict['MEM_INFO'])
		self.sysSettings_dict = self.convertOIDToLocalOIDRepr(allCounters_dict['SYS_INFO'])

	
	# Helper method that converts STD OID into a tuple representation
	def convertOIDToLocalOIDRepr(self, cfgOID_dict):
		# convert a std OID string representation into a tuple of ints representation
		# eg: "0.1.2.3.4.5" -> (0, 1, 2, 3, 4, 5)
		for oidName, oidValue in cfgOID_dict.iteritems():
			cfgOID_dict[oidName] = tuple(map(int, oidValue.split('.')))
		return cfgOID_dict

	def read(self, getCpuFlag=True, getMemFlag=True, getSysFlag=False):
		resultList = list()

		if getCpuFlag:
			cpu = self.getCPU()
			resultList.append(cpu)
		
		if getMemFlag:
			mem = self.getMEM()
			resultList.append(mem[0])
			resultList.append(mem[1])
			resultList.append(mem[3])
			resultList.append(mem[4])

		if getSysFlag:
			sys = self.getSYS()
			for counter in sys:
				resultList.append(counter)

		return resultList

	# SYS query
	def getSYS(self):
		sysSnapshoot = self.sysSnapshoot()

		#self.printSYS(sysSnapshoot)
		return sysSnapshoot
		
	def sysSnapshoot(self):
		sysTmp_dict = self.query(self.sysSettings_dict)
		sysTmp_dict = self.corelateCounterNameWithResult(self.sysSettings_dict, sysTmp_dict)

		sysName = sysTmp_dict['sysname']
		sysDesc = sysTmp_dict['sysdescr']
		sysUpTm = str(timedelta(seconds=int(sysTmp_dict['hrsystemuptime'])/100))
		sysDate = sysTmp_dict['syscdatetime']

		return [sysName, sysDesc, sysUpTm, sysDate]

	# CPU query
	def getCPU(self):
		cpuSnapshoot1 = self.cpuSnapshoot()
		cpuSnapshoot2 = [0, 0, 0, 0]
		while sum(cpuSnapshoot2) <= 0:
			sleep(5)
			cpuSnapshoot2 = self.cpuSnapshoot()
			for i in range(len(cpuSnapshoot1)):
				cpuSnapshoot2[i] -= cpuSnapshoot1[i]
		cpu = round(100 - cpuSnapshoot2[len(cpuSnapshoot2)-1] * 100.00 / sum(cpuSnapshoot2), 2)

		#self.printCPU(cpu)
		return cpu

	def cpuSnapshoot(self):
		cpuTmp_dict = self.query(self.cpuSettings_dict)
		cpuTmp_dict = self.corelateCounterNameWithResult(self.cpuSettings_dict, cpuTmp_dict)

		cpuUser = int(cpuTmp_dict['sscpurawuser'])
		cpuNice = int(cpuTmp_dict['sscpurawnice'])
		cpuSyst = int(cpuTmp_dict['sscpurawsystem'])
		cpuIdle = int(cpuTmp_dict['sscpurawidle'])

		return [cpuUser, cpuNice, cpuSyst, cpuIdle]

	# MEM query
	def getMEM(self):
		memSnapshoot = self.memSnapshoot()
		
		memTotal 	= round(memSnapshoot[0] / 1024.0, 2)
		memUsed		= round(memSnapshoot[1] / 1024.0, 2)
		memFree		= round(memSnapshoot[2] / 1024.0, 2)
		swapTotal	= round(memSnapshoot[3] / 1024.0, 2)
		swapUsed	= round(memSnapshoot[4] / 1024.0, 2)
		swapFree	= round(memSnapshoot[5] / 1024.0, 2)

		memBuffered = memSnapshoot[6] / 1024.0
		memChached	= memSnapshoot[7] / 1024.0

		memValues = [memTotal, memUsed, memFree, swapTotal, swapUsed, swapFree, memBuffered, memChached]
		
		#self.printMEM(memValues)
		return memValues

	def memSnapshoot(self):
		memTmp_dict = self.query(self.memSettings_dict)
		memTmp_dict = self.corelateCounterNameWithResult(self.memSettings_dict, memTmp_dict)

		memTotal	= int(memTmp_dict['memtotalreal'])
		memFree		= int(memTmp_dict['memavailreal'])
		memUsed		= memTotal - memFree

		swapTotal	= int(memTmp_dict['memtotalswap'])
		swapFree	= int(memTmp_dict['memavailswap'])
		swapUsed	= swapTotal - swapFree

		memBuffered	= int(memTmp_dict['membuffer'])
		memChached	= int(memTmp_dict['memcached'])

		return [memTotal, memUsed, memFree, swapTotal, swapUsed, swapFree, memBuffered, memChached]

	# Corelate retrned values with the requested names counters
	def corelateCounterNameWithResult(self, namesDict, resultsDict):
		finalDict = dict()
		for key_name, oid_name in namesDict.iteritems():
			finalDict[key_name] = None
			for oid, val in resultsDict.iteritems():
				if str(oid_name) == str(oid):
					#print '%s = %s' % (key_name, val)
					finalDict[key_name] = val
		return finalDict

	# Query counters using SNMP
	def query(self, oidCountersDict):
		resultsDict = dict()

		# SNMP protocol version to use
		pMod = api.protoModules[api.protoVersion1]
		
		# Build PDU
		reqPDU = pMod.GetRequestPDU()
		pMod.apiPDU.setDefaults(reqPDU)
		
		# Create a tuple of OIDs tuples
		oidList = list()
		for oid in oidCountersDict.values():
			oidList.append((oid, pMod.Null()))
		OIDs = tuple(oidList)
		
		pMod.apiPDU.setVarBinds(reqPDU, (OIDs))

		# Build message
		reqMsg = pMod.Message()
		pMod.apiMessage.setDefaults(reqMsg)
		pMod.apiMessage.setCommunity(reqMsg, 'public')
		pMod.apiMessage.setPDU(reqMsg, reqPDU)

		def cbTimerFun(timeNow, startedAt=time()):
			if timeNow - startedAt > self.snmpTimeout:
				transportDispatcher.jobFinished(1)
				raise SNMPTimeOutError("The host %s has not responded in the specified timeout of %ss!" % (self.host, self.snmpTimeout))
    
		def cbRecvFun(transportDispatcher, transportDomain, transportAddress, wholeMsg, reqPDU=reqPDU):
			while wholeMsg:
				rspMsg, wholeMsg = decoder.decode(wholeMsg, asn1Spec=pMod.Message())
				rspPDU = pMod.apiMessage.getPDU(rspMsg)
				# Match response to request
				if pMod.apiPDU.getRequestID(reqPDU)==pMod.apiPDU.getRequestID(rspPDU):
					# Check for SNMP errors reported
					errorStatus = pMod.apiPDU.getErrorStatus(rspPDU)
					if errorStatus:
						print errorStatus.prettyPrint()
						raise SNMPoIDNotSupported("%s: An requested OID is not supported by this device!" % errorStatus.prettyPrint())
					else:
						for oid, val in pMod.apiPDU.getVarBinds(rspPDU):
							#print '%s = %s' % (oid.prettyPrint(), val)
							resultsDict[str(oid)] = str(val)

					transportDispatcher.jobFinished(1)
			return wholeMsg

		transportDispatcher = AsynsockDispatcher()
		transportDispatcher.registerTransport(udp.domainName, udp.UdpSocketTransport().openClientMode())
		transportDispatcher.registerRecvCbFun(cbRecvFun)
		transportDispatcher.registerTimerCbFun(cbTimerFun)
		transportDispatcher.sendMessage(encoder.encode(reqMsg), udp.domainName, (self.host, int(self.port)))
		transportDispatcher.jobStarted(1)
		transportDispatcher.runDispatcher()
		transportDispatcher.closeDispatcher()

		return resultsDict

	# printing stuff
	def printSYS(self, sysSnapshoot):
		print '\nName: %s' %sysSnapshoot[0]
		print 'Desc: %s' %sysSnapshoot[1]
		print 'UpTm: %s' %sysSnapshoot[2]
		print 'Date: %s' %sysSnapshoot[3]

	def printCPU(self, cpu):
		print "\nCPU: %s%%" % cpu

	def printMEM(self, memSnapshoot):
		memTotal 	= memSnapshoot[0]
		memUsed		= memSnapshoot[1]
		memFree		= memSnapshoot[2]
		swapTotal	= memSnapshoot[3]
		swapUsed	= memSnapshoot[4]
		swapFree	= memSnapshoot[5]

		memBuffered = memSnapshoot[6]
		memChached	= memSnapshoot[7]

		print "\n%s %s %s %s" % ('Mem'.ljust(10), 'Total'.ljust(10), 'Used'.ljust(10), 'Free'.ljust(10))
		print "%s %s %s %s" % ('RAM'.ljust(10), str(memTotal).ljust(10), str(memUsed).ljust(10), str(memFree).ljust(10))
		print "%s %s %s %s" % ('SWAP'.ljust(10), str(swapTotal).ljust(10), str(swapUsed).ljust(10), str(swapFree).ljust(10))

		ramUsedPercent	= (memUsed - memBuffered - memChached) * 1.0 / memTotal * 100

		print "\nUsed memory: %.1f%%" % ramUsedPercent


# SNMP exeptions	
class SNMPTimeOutError(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class SNMPoIDNotSupported(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


if __name__ == '__main__':
	snmp = SNMPQuery('95.76.70.39')
	while(True):
		print snmp.read()
