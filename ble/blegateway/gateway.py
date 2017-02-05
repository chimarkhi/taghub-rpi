import datetime
from collections import defaultdict
import logging


class GatewayParamsStatic:
	## static parameters
	NAME  = 'dev_device_2' 
	WHITELISTREAD_INTERVAL = 6			## hours in which whitelist is updated 		
	SAS_KEY = """SharedAccessSignature sr=tbox-dev-hub.azure-devices.net&sig=KgDCAikL41mUAp12slI61usFc2VlEfG9p5yK1fpZMUE%3D&se=1514369868&skn=iothubowner"""
	IOTHUB = 'tbox-dev-hub.azure-devices.net'
	POST_HEADERS = {'Authorization' : SAS_KEY, 'Content-Type' : 'application/json'}
	DATA_LINK = "https://"+IOTHUB+"/devices/"+NAME+"/messages/events?api-version=2016-02-03"	
	MQTT_USERNAME =IOTHUB+"/"+NAME+"/"+"api-version=2016-11-14"
	LOGFILE = "/home/pi/tagbox/logs/log_blemaster"+NAME+".txt"
	WHITELIST_FILE = "/home/pi/tagbox/ble/blegateway/whitelist"
	WHITELIST_TYPES = ["WL_1","WL_2","WL_3"]	
	GATEWAYPARAMS_FILE = "/home/pi/tagbox/ble/blegateway/GatewayParams.py"

	## Parameters that  can be updated from server
	SCAN_WINDOW = 12					## seconds the scan window is open for
	SCAN_INTERVAL = 30					## seconds scan interval 
	PAYLOAD_INTERVAL = 15				## intervals (seconds) at which scanning window is opened
	UPLOAD_INTERVAL = PAYLOAD_INTERVAL
	PACKET_SIZE = 3500					## bytes, max payload size
	MAX_PACKET_UNITS = 50				## max data points in one payload
	DBFLUSH_INTERVAL = 6				## hours, interval at which db is flushed of data older than KEEPDATA_DAYS 
	KEEPDATA_DAYS = 4					## days till which data is archived
	MAX_PROBECON_ATTEMPTS = 5		## max connect attempts to a peripheral
	POST_TIMEOUT = 120					## seconds, post request timeout
	MQTT_KEEPALIVE = 60 					## seconds for which the connection is kept alive 	
	LOGLEVEL = 10							## logging level
	READNRG = 0							## read modbus for energy data
	WHITELIST_ENABLE = 3					## 0,1,2,3 enable whitelisting levels
	COMMTYPE = "MQTT" 					## HTTPS, MQTT 

	def update(self, GwPrDict):
		keylist = GwPrDict.keys()
		if 'ScWn' in keylist : self.SCAN_WINDOW = GwPrDict['ScWn']	 			## seconds the scan window is open for
		if 'ScIn' in keylist : self.SCAN_INTERVAL = GwPrDict['ScIn']					## seconds scan interval 
		if 'Upin' in keylist : self.PAYLOAD_INTERVAL = GwPrDict['UpIn'] 				## intervals (seconds) at which scanning window is opened	
		if 'Upin' in keylist : self.UPLOAD_INTERVAL = PAYLOAD_INTERVAL
		if 'PkSz' in keylist : self.PACKET_SIZE = GwPrDict['PkSz']						## bytes, max payload size
		if 'PkNo' in keylist : self.MAX_PACKET_UNITS = GwPrDict['PkNo']				## max data points in one payload
		if 'DbIn' in keylist : self.DBFLUSH_INTERVAL = GwPrDict['DbIn']				## hours, interval at which db is flushed of data older than KEEPDATA_DAYS 
		if 'DbKp' in keylist : self.KEEPDATA_DAYS = GwPrDict['DbKp']					## days till which data is archived
		if 'CnAt' in keylist : self.MAX_PROBECON_ATTEMPTS = GwPrDict['CnAt']		## max connect attempts to a peripheral
		if 'UpTO' in keylist : self.POST_TIMEOUT = GwPrDict['UpTO']					## seconds, post request timeout
		if 'MQKA' in keylist : self.MQTT_KEEPALIVE = GwPrDict['MQKA'] 					## seconds for which the connection is kept alive 	
		if 'LogL' in keylist : self.LOGLEVEL = GwPrDict['LogL']						## logging level
		if 'NrgEn' in keylist : self.READNRG = GwPrDict['NrgEn']							## read modbus for energy data
		if 'WLEn' in keylist : self.WHITELIST_ENABLE = GwPrDict['WLEn']					## 0,1,2,3 enable whitelisting levels
		if 'CmTy' in keylist : self.COMMTYPE = GwPrDict['CmTy'] 						## HTTPS, MQTT 
	

class Gateway:
	def __init__(self):
		self.ID = GatewayParams.NAME
	
	def isPower(self):
		## Add power supply detection 
		return str(1)
		
	def batt(self):
		## Add battery level detection
		return str(100)
	
	def payload(self):
		gwInfo = defaultdict(dict)
		gwInfo['GwId'] 	= self.ID
		gwInfo['GwTs'] 	= datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
		gwInfo['GwIsPwr'] =  self.isPower() 
		gwInfo['GwBat'] = self.batt()
		return gwInfo
		
