import datetime
from collections import defaultdict
import logging

class GatewayParams:
	NAME  = 'dev_device_2' 
	SCAN_WINDOW = 10				## seconds the scan window is open for
	SCAN_INTERVAL = 20				## intervals (seconds) at which scanning window is opened
	UPLOAD_INTERVAL = 30

	PACKET_SIZE = 3500
	MAX_PACKET_UNITS = 50
	DBFLUSH_INTERVAL = 6
	KEEPDATA_DAYS = 4

	MAX_PROBECON_ATTEMPTS = 5

	POST_TIMEOUT = 120
	SAS_KEY = """SharedAccessSignature sr=tbox-dev-hub.azure-devices.net&sig=KgDCAikL41mUAp12slI61usFc2VlEfG9p5yK1fpZMUE%3D&se=1514369868&skn=iothubowner"""
	IOTHUB = 'tbox-dev-hub.azure-devices.net'
	POST_HEADERS = {'Authorization' : SAS_KEY, 'Content-Type' : 'application/json'}
	DATA_LINK = "https://"+IOTHUB+"/devices/"+NAME+"/messages/events?api-version=2016-02-03"

	LOGFILE = "/home/pi/tagbox/logs/log_blemaster"+NAME+".txt"
	LOGLEVEL = logging.DEBUG

	READNRG = False

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
		
