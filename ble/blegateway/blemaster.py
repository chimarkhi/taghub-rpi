#!/usr/bin/python
import bluepy.btle as btle
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import logging
import os
import logging.config
import requests

import bledb
import GatewayParams
from gateway import GatewayParamsStatic, LOG_SETTINGS
from scan import ScanDelegate
from cappec import CappecPeripheral
from ankhmaway import AMScanHandler
from minew import MinewScanHandler, MinewUUIDS
from veritek import VeritekVips84

manuNameCappec = "59002d01589086ea01"
typeManuData = 255
typeComplete16bServices = 3
typeCompleteLocalName = 9
cappecAdvName = "Cappec Blaze"
manuNameAM = "4c000215ebefd08370a247c89837e7b5634df"

sched = BlockingScheduler()
probe = None

@sched.scheduled_job('interval',hours = GatewayParams.WHITELISTREAD_INTERVAL)
def readWhitelist():
	whitelistMaster =[]	
	whitelst = []
	for wlType in GatewayParamsStatic.WHITELIST_TYPES:
		try:
			with open(GatewayParamsStatic.WHITELIST_FILE + wlType+".txt","r") as whitelistFile:
				macidList = [line.split(" ")[0] for line in whitelistFile]
			whitelist = [macid.lower().replace(":","") for macid in macidList]
			logger.debug("Whitelist %s elements %s", wlType, whitelist)
		except IOError as ex:
			whitelist = []
			logger.debug("Whitlist file of type %s not present : %s", wlType, ex)		
		except Exception as ex:
			whitelist = []
			logger.exception("Error in reading whitelist %s: %s", wlType, ex)
		finally:
			# if wlType in GatewayParamsStatic.WHITELIST_TYPES[:GatewayParams.WHITELIST_ENABLE ] :							
			whitelistMaster.extend(whitelist)
	logger.debug("Whitelisting level : %s; Whitelist elements: %s", GatewayParams.WHITELIST_ENABLE, whitelistMaster)
	logger.info("No. of devices in whitelist level %s are %d", GatewayParams.WHITELIST_ENABLE, len(whitelistMaster))
	global whitelistGlobal 
	if len(whitelistMaster) != 0:
		whitelistGlobal = whitelistMaster
	return whitelistMaster

@sched.scheduled_job('interval',seconds = GatewayParams.SCAN_INTERVAL)
def scanParse():
	
	## start scan using delegate for scanWindow seconds
	try:
		scanner = btle.Scanner().withDelegate(ScanDelegate())
		devices = scanner.scan(GatewayParams.SCAN_WINDOW)
	
	except Exception, ex:
		devices = []
		os.system("sudo hciconfig hci0 reset")
		logger.exception("Exception in BLE scanning: %s",ex)
		time.sleep(5)
	
	if GatewayParams.WHITELIST_ENABLE :	
		whitelistedDevices = [dev for dev in devices if dev.addr.replace(":","") in whitelistGlobal]
	else:
		whitelistedDevices = devices	
	
	logger.info("No. of devices scanned are %d", len(devices))
	logger.info("No. of scanned devices in whitelist are %d", len(whitelistedDevices))

	## iterate through devices 
	for dev in whitelistedDevices:
		conTries = GatewayParams.MAX_PROBECON_ATTEMPTS

		# identifying Cappec probe out of scanned devices and then fetching data
		if dev.getValueText(typeCompleteLocalName) == cappecAdvName:	
			while conTries > 1:	
				try:
					probe = False
					probe = CappecPeripheral(dev)
					if probe:
						probe.pushToDB()
						logger.info('Probe connected in %d attempts',(GatewayParams.MAX_PROBECON_ATTEMPTS-conTries))
						conTries = 0
				except Exception, ex:
					conTries -= 1
					logger.exception("Exception in Probe (%s) connection:%s",dev.addr, ex)
				finally:
					if probe:
						probe.disconnect()
					#print conTries	
					
		
		# identifying AM Temp/RH tag out of scanned devices and then fetching data
		elif str(dev.getValueText(typeManuData))[0:37]  == manuNameAM:
			try:
				amNode = AMScanHandler(dev)
				##print amNode.getTemp(), amNode.getHumid(), amNode.getBatt()
				amNode.pushToDB()
			except Exception, ex:
				logger.exception("Exception in AM (%s) data handling: %s",dev.addr, ex)


		# identifying Minew S1 Extreme Temp/RHtag out of scanned devices and then fetching data
		elif MinewUUIDS.S1_SERVICE in dev.serviceData.keys() :
			try:
				minewNode = MinewScanHandler(dev)
				minewNode.pushToDB()
			except Exception, ex:
				logger.exception("Exception in MInew S1(%s) data handling: %s",dev.addr, ex)

		# identifying Door Activity Sensors  out of scanned devices and then fetching data
		elif MinewUUIDS.DOORACTSERVICE in dev.serviceData.keys() :
			try:
				minewNode = MinewScanHandler(dev)
				minewNode.pushDoorActToDB()
			except Exception, ex:
				logger.exception("Exception in Door Sensor (%s) data handling: %s",dev.addr, ex)
		
	# Reading Veritek's Energy meter Modubus and fetching data	
	if GatewayParams.READNRG == 1 :
		try:
			nrgMeter = VeritekVips84('/dev/ttyUSB0', 1)    
		    	nrgMeter.debug = False
			nrgMeter.pushToDB()
		except Exception, ex:
			logger.exception("Exception in Energy Meter data handling : %s", ex)


@sched.scheduled_job('interval',seconds = GatewayParams.UPLOAD_INTERVAL)
def packetCreation():
	bledb.createPacket()
	logger.info('Payload created in DB')	


@sched.scheduled_job('interval',seconds = GatewayParams.UPLOAD_INTERVAL)
def dBToServer():
	upStatus = bledb.uploadPayload()
	logger.info('Payload uploaded with response %d', upStatus)	


@sched.scheduled_job('interval',hours = GatewayParams.DBFLUSH_INTERVAL)
def dBFlush():	
	dber = bledb.dbQuorer()
	tab = dber.getTableNames()
	
	for table in tab:
		dber.delOldRows(table,GatewayParams.KEEPDATA_DAYS)
		logger.info('Deleted Records older than %d days from %s', GatewayParams.KEEPDATA_DAYS, table)
	dber.close()


def file_upload(upFile):
	try:
		payload = {'file': open(upFile, 'rb'),
		'GwId': GatewayParamsStatic.NAME}

		r = requests.post(GatewayParamsStatic.D2C_LOG_LINK, 
				files=payload,
				timeout=GatewayParams.POST_TIMEOUT)
		upDone = r.status_code
	except Exception as ex:
		upDone = 0
		logger.exception('Exception in uploading log file %s: %s',upFile,ex)
	finally:
		if divmod(upDone,100)[0] == 2:	
			logger.info('Log file %s uploaded with status : %d',upFile,upDone)
		else:
			logger.error('Log file upload failed with status: %d',upFile, upDone)


@sched.scheduled_job('interval',hours = GatewayParams.LOG_UPLOAD_INTERVAL)
def logs_upload():
	file_upload(GatewayParamsStatic.LOGFILE_BLE)
	file_upload(GatewayParamsStatic.LOGFILE_MQTT)


if __name__ ==  "__main__" :
	logging.config.fileConfig('./logging.conf',
				disable_existing_loggers = False,
				defaults={'logFileName'	:GatewayParamsStatic.LOGFILE_BLE,
					  'logLevel'	:GatewayParams.LOGLEVEL,
					  'logFileSize' :GatewayParams.LOGFILE_SIZE,
					  'logBackupCount':GatewayParams.LOG_BACKUPS })
					  
	logger = logging.getLogger('__main__')	

	logger.info('Logging started')	
	whitelistGlobal = readWhitelist()

	bledb.createDB()		
	logger.info('Created Telemetry DB')

	logger.info('Opening First scan window')
	scanParse()

	logger.info('Starting Scheduler ')
	sched.start()

