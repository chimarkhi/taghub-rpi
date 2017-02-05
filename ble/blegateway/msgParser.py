import json
import logging
import datetime
import os

import blemaster
import GatewayParams
from gateway import GatewayParamsStatic


cmTyWL = 'WLs'
cmTyGP = 'GwPr'
gatewayType = "pi"

class CommandAck:
	GwId = GatewayParamsStatic.NAME
	GwTs =  datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
	def __init__(self,msgIn):
		self.CmId = msgIn["CmId"]
		self.CmSt = 0
	def updateSt(self,success):
		self.CmSt = success
	def updateTs(self):
		self.GwTs = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

def inMQTTJSON(payloadJSON):
	msg = json.loads(payloadJSON)
	c2dmsgJsonPretty = json.dumps(msg,indent=4, sort_keys=True)	
	print c2dmsgJsonPretty
	
	cmAck = CommandAck(msg)

	try:
		commandId = msg["CmId"]	
		commandGwTy = msg["GwTy"]
		commandType = msg["CmTy"]
		commandTs = msg["CmTs"]	
		commandValid = True
	except:
		commandId = None
		commandGwTy = None
		commandType = None
		print "C2D command does not have Id/GwTy/Ty/Ts data ", ex
		logging.error("Exception updating whitelist %s", ex)
		commandValid = False

	try: 
		commandData = msg["CmData"]
	except :
		commandData = None
		print "C2D command does not have Data field ", ex
		logging.error("C2D command has no Data field %s", ex)
			

	if commandGwTy == gatewayType and commandValid == True :
		if commandType == cmTyWL:
			try:
				cmSuccess = createWLTxt(commandData)
				cmAck.updateSt(cmSuccess)
			except Exception as ex:
				print "Exception updating whitelist ", wlType, ex
				logging.error("Exception updating whitelist %s:%s", wlType, ex)
			finally:
				cmAck.updateTs()
		
		elif commandType == cmTyGP:
			try:
				cmSuccess = createGPTxt(commandData)
				cmAck.updateSt(cmSuccess)			
			except Exception as ex:
				print "Exception updating  gateway params ", wlType, ex
				logging.error("Exception updating gateway params %s:%s", wlType, ex)
			finally:
				cmAck.updateTs()
		else :
			cmAck.updateTs()
			print "Command Type invalid ", wlType, ex
			logging.warning("Command Type invalid", wlType, ex)			
	else :
		cmAck.updateTs()
		print "Invalid C2D command "
		logging.warning("Invalid C2D command")

	return cmAck
		

def createWLTxt(cmData):
	for wlType in cmData.keys() :
		if wlType in GatewayParamsStatic.WHITELIST_TYPES:
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
				logging.info("Whitelist type %s  updated", wlType)
				cmSuccess = 1 
			except Exception as ex:
				print "Exception updating whitelist ", wlType, ex
				logging.error("Exception updating whitelist %s: %s", wlType, ex)
				cmSuccess = 0
		else :
			print "Command has incorrect  ", wlType, ex
			logging.error("Exception updating whitelist %s: %s", wlType, ex)
			cmSuccess = 0
	if cmSuccess:
		r = os.system("rename 's/txt_bkup/txt/g' " + GatewayParamsStatic.WHITELIST_FILE +"*.txt_bkup") 
		cmSuccess = 1 if r == 0 else  0 
	return cmSuccess
		



def createGPTxt(gpIn):
	gpFile = GatewayParamsStatic.GATEWAYPARAMS_FILE
	gpFile = "/home/pi/tagbox/ble/blegateway/testOUT.py"
		
	for key,value in gpIn.items() :
		if key == 'ScWn'  : updateTxT("SCAN_WINDOW",key,value,gpFile) 	 			## seconds the scan window is open for
		elif key == 'ScIn'  : updateTxT("SCAN_INTERVAL",key,value,gpFile)					## seconds scan interval 
		elif key == 'Upin'  : updateTxT("PAYLOAD_INTERVAL",key,value,gpFile) 				## intervals (seconds) at which scanning window is opened	
		elif key == 'Upin'  : updateTxT("UPLOAD_INTERVAL",key,value,gpFile)
		elif key == 'PkSz' : updateTxT("PACKET_SIZE",key,value,gpFile)						## bytes, max payload size
		elif key =='PkNo' : updateTxT("MAX_PACKET_UNITS",key,value,gpFile)				## max data points in one payload
		elif key == 'DbIn' : updateTxT("DBFLUSH_INTERVAL",key,value,gpFile)				## hours, interval at which db is flushed of data older than KEEPDATA_DAYS 
		elif key == 'DbKp' : updateTxT("KEEPDATA_DAYS",key,value,gpFile)					## days till which data is archived
		elif key =='CnAt'  : updateTxT("MAX_PROBECON_ATTEMPTS",key,value,gpFile)		## max connect attempts to a peripheral
		elif key =='UpTO' : updateTxT("POST_TIMEOUT",key,value,gpFile)					## seconds, post request timeout
		elif key =='MQKA' : updateTxT("MQTT_KEEPALIVE",key,value,gpFile) 					## seconds for which the connection is kept alive 	
		elif key =='LogL'  : updateTxT("LOGLEVEL",key,value,gpFile)						## logging level
		elif key =='NrgEn'  : updateTxT("READNRG",key,value,gpFile)							## read modbus for energy data
		elif key =='WLEn'  : updateTxT("WHITELIST_ENABLE",key,value,gpFile)					## 0,1,2,3 enable whitelisting levels
		elif key =='CmTy'  : updateTxT("COMMTYPE",key,value,gpFile)						## HTTPS, MQTT 
	

def updateTxT(oldStr, key, value, fileName):
	try:
		f = open(fileName,"w+") 
		param_exists =0
		for line in f:
			if oldStr in line:
				f.write(oldStr+" = "+str(value))
				param_exists = 1
				print("Gateway Parameter %s updated to %s",key,value)
				logging.info("Gateway Parameter %s updated to %s",key,value)
	except Exception as ex:
		logging.error("Exception in Gateway Parameter update : %s",ex)
		print("Exception in Gateway Parameter update : %s",ex)
	finally: 
		f.close()
