import datetime
from collections import defaultdict
import logging

class GatewayParams:
	NAME  = 'tb_GW_7' 
	SCAN_WINDOW = 10				## seconds the scan window is open for
	SCAN_INTERVAL = 60				## intervals (seconds) at which scanning window is opened
	UPLOAD_INTERVAL = 60

	PACKET_SIZE = 2000
	MAX_PACKET_UNITS = 25
	DBFLUSH_INTERVAL = 6
	KEEPDATA_DAYS = 4

	MAX_PROBECON_ATTEMPTS = 5

	POST_TIMEOUT = 120
	SAS_KEY = """SharedAccessSignature sr=tbox-iot-hub2.azure-devices.net&sig=e0Fs4aL8qHRW9qY2LbkBUyDk1Xwss8rH%2BmjaY6uJmnc%3D&se=1511703639&skn=iothubowner"""
	IOTHUB = 'tbox-iot-hub2.azure-devices.net'
	POST_HEADERS = {'Authorization' : SAS_KEY, 'Content-Type' : 'application/json'}
	DATA_LINK = "https://"+IOTHUB+"/devices/"+NAME+"/messages/events?api-version=2016-02-03"

	LOGFILE = "/home/pi/tagbox/logs/log_blemaster.txt"
	LOGLEVEL = logging.DEBUG

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
		
