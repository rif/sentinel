from ConfigParser import SafeConfigParser

INI_FILE = "deviceOIDs.ini"

class Parser(object):
	def __init__(self, iniFileName = INI_FILE):
		self.scp = SafeConfigParser()
		self.iniFileName = iniFileName
		with open(iniFileName) as fp:
			self.scp.readfp(fp)
	
	# Return a dictionary for which sections are the keys and the values are dict of settings and values from that section
	def getDictOfAllSectionsAndSettings(self):
		return self.buildSectionDict()
	
	# Return a dict of all settings and values contained in the config file, but uncategorized by sections
	def getDictOfBulkSettings(self):
		bulkDict = dict()
		for sectionDict in self.getDictOfAllSectionsAndSettings().itervalues():
			for settingName, settingValue in sectionDict.iteritems():
				bulkDict[settingName] = settingValue
		return bulkDict
		
	# Return a dictionary of sections keys whith sub dict of setting names and values
	def buildSectionDict(self):
		sectionDict = dict()
		for configSection in self.getConfigSections():
			sectionDict[configSection] = self.buildOptionsDict(configSection)
		return sectionDict

	# Return a dictionary of settingNames and values from a specified section
	def buildOptionsDict(self, sectionName):
		settingsDict = dict()
		for settingName in self.getConfigOptions(sectionName):
			settingsDict[settingName] = self.getSetting(sectionName, settingName)
		return settingsDict

	# Gets all section defiend in the config file
	def getConfigSections(self):
		return self.scp.sections()

	# Gets all setting names contained in one section
	def getConfigOptions(self, sectionName):
		return self.scp.options(sectionName)

	# Get one setting from config file specified by section and setting name
	def getSetting(self, sectionName, settingName):
		return self.scp.get(sectionName, settingName)


if __name__ == '__main__':
	p = Parser()
	for sectionName, settingsDict in p.getDictOfAllSectionsAndSettings().iteritems():
		print '\nSECTION: %s' % sectionName
		for settingName, settingValue in settingsDict.iteritems():
			print '\t%s = %s' % (settingName.ljust(15), settingValue)
	
	print 
	for key, value in p.getDictOfBulkSettings().iteritems():
		print '\t%s = %s' % (key.ljust(15), value)