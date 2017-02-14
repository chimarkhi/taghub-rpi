import datetime
from collections import defaultdict
import logging
import subprocess

## Gateway's static parameters
class GatewayParamsStatic:
	NAME  = 'dev_device_2' 
	WHITELISTREAD_INTERVAL = 6			## hours in which whitelist is updated 		
	SAS_KEY = """SharedAccessSignature sr=tbox-dev-hub.azure-devices.net&sig=KgDCAikL41mUAp12slI61usFc2VlEfG9p5yK1fpZMUE%3D&se=1514369868&skn=iothubowner"""
	IOTHUB = 'tbox-dev-hub.azure-devices.net'
	POST_HEADERS = {'Authorization' : SAS_KEY, 'Content-Type' : 'application/json'}
	DATA_LINK = "https://"+IOTHUB+"/devices/"+NAME+"/messages/events?api-version=2016-02-03"	
	MQTT_USERNAME =IOTHUB+"/"+NAME+"/"+"api-version=2016-11-14"
	LOGFILE_BLE = "/home/pi/tagbox/logs/log_blemaster"+NAME+".txt"
	LOGFILE_MQTT = "/home/pi/tagbox/logs/log_blemaster"+"_MQTT"+".txt"
	WHITELIST_FILE = "/home/pi/tagbox/ble/blegateway/whitelist"
	WHITELIST_TYPES = ["Wl_1","Wl_2","Wl_3"]	
	GATEWAYPARAMS_FILE = "/home/pi/tagbox/ble/blegateway/GatewayParams.py"


## for parsing C2D message
class GatewayParamsC2D:
	GATEWAY_TYPE = "pi"
	COMMAND_ID_KEY = 'CmId'
	GATEWAY_TYPE_KEY = "GwTy"
	COMMAND_TYPE_KEY = "CmTy"
	COMMAND_TS_KEY ="CmTs"
	COMMAND_DATA_KEY = "CmData"
	GATEWAY_ID_KEY =  "GwId"


## Parameters that  can be updated from server
class GatewayParamsDynamic:
	SCAN_WINDOW = 12					## seconds the scan window is open for
	SCAN_INTERVAL = 30					## seconds scan interval 
	UPLOAD_INTERVAL = 15				## intervals (seconds) at which payload is created and posted
	PACKET_SIZE = 3500					## bytes, max payload size
	MAX_PACKET_UNITS = 50				## max data points in one payload
	MQTT_KEEPALIVE = 60 					## seconds for which the connection is kept alive 	
	WHITELIST_ENABLE = 3					## 0,1,2,3 enable whitelisting levels

## Gateway type (Android/Pi) specific parameters (can be updated from server)
class GatewayParamsSpecific:
	DBFLUSH_INTERVAL = 6				## hours, interval at which db is flushed of data older than KEEPDATA_DAYS 
	KEEPDATA_DAYS = 4					## days till which data is archived
	MAX_PROBECON_ATTEMPTS = 5		## max connect attempts to a peripheral
	POST_TIMEOUT = 120					## seconds, post request timeout
	LOGLEVEL = 10							## logging level
	COMMTYPE = "MQTT" 					## HTTPS, MQTT 

## Peripheral control parameters (can be updated from server)
class GatewayPeripheralCtrl:
	READNRG = 0							## read modbus for energy data
	BLE_ENABLE = 1							## Enable ble radio
		

class Gateway:
	def __init__(self):
		self.ID = GatewayParamsStatic.NAME
	
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

def gatewayAction(actionIn):
	for key in actionIn.keys():
		if key == cmKeyAppRestart :
			cmSuccess = appRestart()
		elif key == cmKeyGwRestart:
			cmSuccess = reboot()
		else :
			cmSuccess = 0			
			print "No actionable gateway action found"
			logging.info("No actionable gateway action found")
	return cmSuccess

def appRestart():
	try:
		blemasterPID = map(int,subprocess.check_output(["pgrep","-f", "sudo python blemaster.py"]).split())
		if len[blemasterPID] is not 0:
			for i in enumerate(blemasterPID):			
				os.kill(pid[i],signal.SIGTERM)
		logging.info("All blemaster.py process killed. Relevant pids found %d", len(blemasterPID))
		blemasterProcess = subprocess.Popen(["sudo","python","blemaster.py"])
		logging.info("blemaster process started ")	
		cmSuccess = 1
	except subprocess.CalledProcessError:
		logging.info("blemaster process not running ")	
		blemasterProcess = subprocess.Popen(["sudo","python","blemaster.py"])
		logging.info("blemaster process started ")	
		cmSuccess = 1
	except Exception as ex:
		logging.error("Exception during process restart : %s",ex)
		cmSuccess = 0
	return cmSuccess


def reboot():
	try:
		blemasterProcess = subprocess.Popen(["sudo","reboot"])
		cmSuccess = 1
	except Exception as ex:
		logging.error("Exception during gateway reboot : %s",ex)
		print("Exception during gateway reboot : %s",ex)
		cmSuccess = 0
	return cmSuccess

	
