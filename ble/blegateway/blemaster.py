import bluepy.btle as btle
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import logging

import bledb
from gateway import GatewayParams
from scan import ScanDelegate
from cappec import CappecPeripheral
from ankhmaway import AMScanHandler
from minew import MinewScanHandler, MinewUUIDS

manuNameCappec = "59002d01589086ea01"
typeManuData = 255
typeComplete16bServices = 3
typeCompleteLocalName = 9
cappecAdvName = "Cappec Blaze"
manuNameAM = "4c000215ebefd08370a247c89837e7b5634df"

sched = BlockingScheduler()
probe = None

@sched.scheduled_job('interval',seconds = GatewayParams.SCAN_INTERVAL)
def scanParse():
	
	## start scan using delegate for scanWindow seconds
	try:
		scanner = btle.Scanner().withDelegate(ScanDelegate())
		devices = scanner.scan(GatewayParams.SCAN_WINDOW)
			
	except Exception, ex:
		logging.error("Exception in BLE scanning: %s",ex)
	
	## iterate through devices 
	for dev in devices:
		conTries = GatewayParams.MAX_PROBECON_ATTEMPTS

		# identifying Cappec probe out of scanned devices and then fetching data
		if dev.getValueText(typeCompleteLocalName) == cappecAdvName:	
			while conTries > 1:	
				try:
					probe = False
					probe = CappecPeripheral(dev)
					if probe:
						probe.pushToDB()
						logging.info('Probe connected in %d attempts',(GatewayParams.MAX_PROBECON_ATTEMPTS-conTries))
						conTries = 0
				except Exception, ex:
					conTries -= 1
					logging.error("Exception in Probe (%s) connection:%s",dev.addr, ex)
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
				logging.error("Exception in AM (%s) data handling: %s",dev.addr, ex)


		# identifying Minew S1 Extreme Temp/RHtag out of scanned devices and then fetching data
		elif MinewUUIDS.S1_SERVICE in dev.serviceData.keys() :
			try:
				minewNode = MinewScanHandler(dev)
				minewNode.pushToDB()
			except Exception, ex:
				logging.error("Exception in MInew S1(%s) data handling: %s",dev.addr, ex)

		# identifying Door Activity Sensors  out of scanned devices and then fetching data
		elif MinewUUIDS.DOORACTSERVICE in dev.serviceData.keys() :
			try:
				minewNode = MinewScanHandler(dev)
				minewNode.pushDoorActToDB()
			except Exception, ex:
				logging.error("Exception in Door Sensor (%s) data handling: %s",dev.addr, ex)


@sched.scheduled_job('interval',seconds = GatewayParams.UPLOAD_INTERVAL)
def dBToServer():
	bledb.createPacket()
	upStatus = bledb.uploadPayload()
	logging.info('Payload uploaded with response %d', upStatus)	


@sched.scheduled_job('interval',hours = GatewayParams.DBFLUSH_INTERVAL)
def dBFlush():	
	dber = bledb.dbQuorer()
	tab = dber.getTableNames()
	
	for table in tab:
		dber.delOldRows(table,GatewayParams.KEEPDATA_DAYS)
		logging.info('Deleted Records older than %d days from %s', GatewayParams.KEEPDATA_DAYS, table)
	dber.close()


def main() :
	logging.basicConfig(filename=GatewayParams.LOGFILE, filemode = 'w', 
						format='[%(asctime)s] %(levelname)s %(message)s', 
						datefmt='%Y-%m-%d %H:%M:%S',  
						level = GatewayParams.LOGLEVEL)
	logging.info('Logging started')	

	bledb.createDB()		
	logging.info('Created Telemetry DB')

	logging.info('Opening First scan window')
	scanParse()

	logging.info('Starting Scheduler ')
	sched.start()

if __name__ == "__main__":
	main()
