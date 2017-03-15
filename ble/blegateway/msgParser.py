import json
import logging
import datetime
import os
import subprocess

import blemaster
import GatewayParams
from gateway import GatewayParamsStatic, GatewayParamsC2D
import gateway

logger = logging.getLogger(__name__)

cmTyWL = 'Wls'
cmTyGp = 'GwParam'
cmTyGpSp = "GwParamSp"
cmTyGwPerCtrl = "GwPeripheralCtrl"
cmTyCnData = "CnData"
cmTyGwFunc = "GwFunc"


gatewayType = GatewayParamsC2D.GATEWAY_TYPE
commandIDKey = GatewayParamsC2D.COMMAND_ID_KEY
gatewayTypeKey = GatewayParamsC2D.GATEWAY_TYPE_KEY
commandTypeKey = GatewayParamsC2D.COMMAND_TYPE_KEY
commandTimestampKey = GatewayParamsC2D.COMMAND_TS_KEY 
commandDataKey = GatewayParamsC2D.COMMAND_DATA_KEY

cmKeyRestart = "Restart"
cmValueAppRestart = "AppRestart"
cmValueGwReboot = "GwReboot"


## C2D command to gateway parameter key map
key_map = {'ScWn'  : "SCAN_WINDOW", 	 				## seconds the scan window is open for
	'ScIn'  : "SCAN_INTERVAL",					## seconds scan interval 
	'UpIn'  : "UPLOAD_INTERVAL", 					## intervals (seconds) at which scanning window is opened	
	'PkSz' : "PACKET_SIZE",						## bytes, max payload size
	'PkNo' : "MAX_PACKET_UNITS",					## max data points in one payload
	'MqttKA' : "MQTT_KEEPALIVE", 					## seconds for which the connection is kept alive 	
	'WlEn'  : "WHITELIST_ENABLE",					## 0,1,2,3 enable whitelisting levels

	'DbIn' : "DBFLUSH_INTERVAL",					## hours, interval at which db is flushed of data older than KEEPDATA_DAYS 
	'DbKp' : "KEEPDATA_DAYS",					## days till which data is archived
	'CnAt'  : "MAX_PROBECON_ATTEMPTS",				## max connect attempts to a peripheral
	'UpTO' : "POST_TIMEOUT",					## seconds, post request timeout
	'LogL'  : "LOGLEVEL",						## logging level
	'LogSz'	: "LOGFILE_SIZE",					## size of logfile before rollover
	'LogBkup':"LOG_BACKUPS",					## number of logfiel backups
	'CommTy'  : "COMMTYPE",						## HTTPS, MQTT 

	'NrgCtrl'  : "READNRG",						## read modbus for energy data
	'BlCtrl'	: "BLE_ENABLE",					## enable gateway's ble radio
	
	'BLEMonInt': "BLEMONITOR_INTERVAL"				## interval at which mqtt service monitors blemaster
	}		

class CommandAck:
	GwId = GatewayParamsStatic.NAME
	GwTs =  datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
	Message = ""
	CmData = ""
	def __init__(self,msgIn):
		try:
			self.CmId = msgIn[commandIDKey]
		## If Command Id isnt present assign default CmId to return message
		except :
			self.CmId = "FFFFFFFF"
		self.CmSt = 0
	def updateSt(self,success):
		self.CmSt = success
	def updateTs(self):
		self.GwTs = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

def inMQTTJSON(payloadJSON):	
	msg = json.loads(payloadJSON)
	c2dmsgJsonPretty = json.dumps(msg,indent=4, sort_keys=True)	

	## Create Command response packet with status intialized to failure (0)	
	cmAck = CommandAck(msg)

	## Parse Command for mandatory fields
	try:
		commandId = msg[commandIDKey]	
		commandGwTy = msg[gatewayTypeKey]
		commandType = msg[commandTypeKey]
		commandTs = msg[commandTimestampKey]	
		commandValid = True
	except Exception as ex:
		commandId = ""
		commandGwTy = ""
		commandType = ""
		print "C2D command does not have Id/GwTy/Ty/Ts data ",ex
		logger.exception("C2D command does not have Id/GwTy/Ty/Ts data: %s", ex)
		commandValid = False

	## Check if Command Data is present
	try: 
		commandData = json.loads(msg[commandDataKey])
	except Exception as ex:
		commandData = None
		print "C2D command does not have Data field ", ex
		logger.exception("C2D command has no Data field %s", ex)
		cmAck.updateTs()
		return cmAck

	## For a valid command with correct gateway type value take actions according to command type
	if commandGwTy == gatewayType and commandValid == True :

		## Create Whitelist text files if type is "WLs" 
		if commandType == cmTyWL:
			try:
				cmSuccess = createWLTxt(commandData)
				cmAck.updateSt(cmSuccess)
			except Exception as ex:
				print "Exception updating whitelist ", ex
				logger.exception("Exception updating whitelist %s", ex)
			finally:
				cmAck.updateTs()

		## Update GatewayParams.py text file if type is "GwParam", 'GwParamSp' or 'GwPeripheralCtrl'. Only dynamic params in this file		
		elif commandType == cmTyGp or commandType == cmTyGpSp or commandType == cmTyGwPerCtrl:
			try:
				cmSuccess = updateParamFile(commandData, GatewayParamsStatic.GATEWAYPARAMS_FILE)
				cmAck.updateSt(cmSuccess)			
			except Exception as ex:
				print "Exception updating  gateway params ", ex
				logger.exception("Exception updating gateway params: %s", ex)
			finally:
				cmAck.updateTs()
		
		## Run the command function as mentioned in GwFunc command 
		elif commandType == cmTyGwFunc :
			try:
				cmSuccess = gatewayAction(commandData)
				cmAck.updateSt(cmSuccess)			
			except Exception as ex:
				print "Exception running gateway action ", ex
				logger.exception("Exception running gateway action: %s", ex)
			finally:
				cmAck.updateTs()

		## If no identifiable command type found in message		
		else:
			print "No actionable Command Type found"
			logger.error("No actionable Command Type found")
			cmAck.updateTs()

	else :		
		print "Invalid C2D command "
		logger.warning("Invalid C2D command")
		cmAck.updateTs()

	return cmAck
		
def gatewayAction(actionIn):
	for key in actionIn.keys():
		if key == cmKeyRestart:
			if actionIn[key] == cmValueAppRestart :
				cmSuccess = gateway.appMonitor(hardRestart=True)
			elif actionIn[key] == cmValueGwRestart:
				cmSuccess = gateway.reboot()
			else :
				cmSuccess = 0			
				print "No actionable gateway action found"
				logger.info("No actionable gateway action found")
	return cmSuccess


def createWLTxt(cmData):
	wlUpList = []	
	osMoveSt = 0
	## Iterate through whitelist types in command
	for wlType in cmData.keys() :
		## Only for valid whitelist types 
		if wlType in GatewayParamsStatic.WHITELIST_TYPES:
			## Write whitelist data in bkup text files. Each whitelist has separate txt file
			try:
				wlList = cmData[wlType]
				whitelistFile = open(GatewayParamsStatic.WHITELIST_FILE+str(wlType)+".txt_bkup","w")
				for i in wlList :
					a = ""
					for v in i.values():
						a = a+v+" "
					whitelistFile.write(str(a)+"\n")
				whitelistFile.close()
				print "Whitelist type  updated", wlType
				logger.info("Whitelist type %s  updated", wlType)
				cmSuccess = 1 
				wlUpList.append(wlType)
			except Exception as ex:
				print "Exception updating whitelist ", wlType, ex
				logger.exception("Exception updating whitelist %s: %s", wlType, ex)
				## Even if any one whitelist file creation fails command action is assumed to fail				
				cmSuccess = 0
		else :
			print "Command has incorrect  whitelist type", wlType
			logger.error("Command has incorrect whitelist type %s", wlType)
			cmSuccess = 0
	## Only if all bkup whitelist files created succesfully 
	if cmSuccess:
		try:
			## Try moving bkup files to main 
			r = os.system("rename -f 's/txt_bkup/txt/g' " + GatewayParamsStatic.WHITELIST_FILE +"*.txt_bkup")
		except Exception as ex:
			r = 256
			print "Exception copying whitlelist .txt_bkup to txt ", ex
			logger.exception("Exception copying .txt_bkup to txt %s", ex)	
	else: 
		r = 256	
	## Command action deemed succesful when all bkup files moved to main successfully	
	cmSuccess = 1 if r == 0 else  0
	return cmSuccess

def updateParamFile(gpIn, filename):
	origFile = filename
	backupFile = filename +"_bkup"
	updatedParamList = []

	with open(origFile,"r") as f:
		lines = f.readlines()
	try:	
		for key,value in gpIn.items() :
			if key in key_map.keys():
				lines = updateLines(key_map[key],key,value,lines); 
				updatedParamList.append(key) 	 			
		with open(backupFile,'w') as f:
			f.writelines(lines)
		cmSuccess = 1
	except Exception as ex:
		print "Exception updating Gateway Params ", ex
		logger.exception("Exception updating Gateway Params %s", ex)	
		cmSuccess = 0
	## Only if bkup gateway parameters file created succesfully 
	if cmSuccess:
		try:
			## Try moving bkup files to main 
			r = os.rename(backupFile, origFile)
			r = 0 
			print "Updated gateway params : ", updatedParamList
			logger.info("Updated gateway params: %s", updatedParamList)	
		except Exception as ex:
			r = 256
			print "Exception copying gateway parameters  .py_bkup to py ", ex
			logger.exception("Exception copying gateway parameters .py_bkup to py %s", ex)	
	else: 
		r = 256	
	## Command action deemed succesful when all bkup files moved to main successfully	
	cmSuccess = 1 if r == 0 else  0
	return cmSuccess
		
def updateLines(oldStr, key, value, lines):
	newLines = []
	try:
		for line in lines:
			if line.startswith(oldStr):
				linearray = line.rsplit()
				linearray[2] = str(value) if type(value) == int else "\""+value+"\""
				linearray.append("\n")
				line = " ".join(linearray)
			newLines.append(line)
	except Exception as ex:
		newLines = lines
		logger.exception("Exception in Gateway Parameter update : %s",ex)
		print("Exception in Gateway Parameter update : %s",ex)
	finally:
		return newLines



			
