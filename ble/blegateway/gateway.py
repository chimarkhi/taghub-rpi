import datetime
from collections import defaultdict
import logging
import subprocess
import os
import signal

import GatewayParams

logger = logging.getLogger(__name__)

## Gateway's static parameters
class GatewayParamsStatic:
	NAME  = "an_pi_0002" 
		#'cd_pi_0001' 
	WHITELISTREAD_INTERVAL = 6			## hours in which whitelist is updated 		
#	SAS_KEY = "SharedAccessSignature sr=iot-hub-cd.azure-devices.net%2Fdevices%2Fcd_pi_0001&sig=FsdTJHA8ZrgY7z51ce06zou9rFfnGkuoa0JhLE5nGfU%3D&se=1520417683"
	SAS_KEY = "SharedAccessSignature sr=iot-hub-an.azure-devices.net%2Fdevices%2Fan_pi_0002&sig=ruIBlaga0B%2F%2BL6X1av6WoR09oczCm%2BDL7lyRbMm2N4Q%3D&se=1521018851"
	IOTHUB = "iot-hub-an.azure-devices.net"
		#'iot-hub-cd.azure-devices.net'
	POST_HEADERS = {'Authorization' : SAS_KEY, 'Content-Type' : 'application/json'}
	DATA_LINK = "https://"+IOTHUB+"/devices/"+NAME+"/messages/events?api-version=2016-02-03"	
	D2C_ACK_LINK = "http://anc2drest.azurewebsites.net/restservice/v1/d2c/cmdresponse"
	D2C_LOG_LINK = "http://anc2drest.azurewebsites.net/restservice/v1/d2c/logfile"
#	D2C_LOG_LINK = "http://104.215.248.40:8080/restservice/v1/d2c/logfile"
	MQTT_USERNAME =IOTHUB+"/"+NAME+"/"+"api-version=2016-11-14"
	LOGFILE_BLE = "/home/pi/tagbox/logs/blemaster_"+NAME+".log"
	LOGFILE_MQTT = "/home/pi/tagbox/logs/mqttservice_"+NAME+".log"
	WHITELIST_FILE = "/home/pi/tagbox/ble/blegateway/whitelist"
	WHITELIST_TYPES = ["Wl_AM","Wl_Door","Wl_Nrg"]	
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
	WHITELIST_ENABLE = 1					## 0,1,2,3 enable whitelisting levels

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


def appMonitor(hardRestart):
	try:
		blemasterPID = map(int,subprocess.check_output(["pgrep","-f", "sudo python blemaster.py"]).split())
		if len(blemasterPID) is not 0 and (hardRestart is True):
			for i in range(len(blemasterPID)):			
				os.kill(blemasterPID[i],signal.SIGTERM)
			logger.info("All blemaster.py processes killed. Relevant pids found %d", len(blemasterPID))
			blemasterProcess = subprocess.Popen(["sudo","python","blemaster.py"],stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
			logger.info("blemaster process started ")	
			cmSuccess = 1
		else: 
			cmSuccess = 0
	except subprocess.CalledProcessError:
		logger.warning("blemaster process not running ")	
		blemasterProcess = subprocess.Popen(["sudo","python","blemaster.py"],stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
		logger.warning("blemaster process started ")	
		cmSuccess = 1
	except Exception as ex:
		logger.exception("Exception during process restart : %s",ex)
		cmSuccess = 0
	return cmSuccess


def reboot():
	try:
		blemasterProcess = subprocess.Popen(["sudo","reboot"])
		cmSuccess = 1
	except Exception as ex:
		logger.exception("Exception during gateway reboot : %s",ex)
		print("Exception during gateway reboot : %s",ex)
		cmSuccess = 0
	return cmSuccess

	
LOG_SETTINGS = {
'version': 1,
'disable_existing_loggers':False,
'handlers': {
    'console': {
        'class': 'logging.StreamHandler',
        'level': 'INFO',
        'formatter': 'detailed',
        'stream': 'ext://sys.stdout',
    },
    'ble_handler': {
        'class': 'logging.handlers.RotatingFileHandler',
        'level': 10,
        'formatter': 'detailed',
        'filename': GatewayParamsStatic.LOGFILE_BLE,
        'mode': 'a',
        'maxBytes': 2*10485760,
        'backupCount': 2,
    },
    'mqtt_handler': {
        'class': 'logging.handlers.RotatingFileHandler',
        'level': GatewayParams.LOGLEVEL,
        'formatter': 'detailed',
        'filename': GatewayParamsStatic.LOGFILE_MQTT,
        'mode': 'a',
        'maxBytes': 2*10485760,
        'backupCount': 2,
    },

},
'formatters': {
    'detailed': {
        'format': '[%(asctime)s] %(name)s %(levelname)s : %(message)s',
	'datefmt': '%Y-%m-%d %H:%M:%S',
    },
    'email': {
        'format': 'Timestamp: %(asctime)s\nModule: %(module)s\n' \
        'Line: %(lineno)d\nMessage: %(message)s',
    },
},
'loggers': {
    'ble': {
        'handlers': ['ble_handler',]
        },
    'mqtt': {
        'handlers': ['mqtt_handler',]
        },

}
}
