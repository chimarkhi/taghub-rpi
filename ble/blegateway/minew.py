import bluepy.btle as btle
import time
import datetime
import sqlite3 as sql
import logging

import bledb

logger = logging.getLogger(__name__)

class MinewUUIDS:
	S1_SERVICE = "ffe1"
	DOORACTSERVICE = 'abcd'
	BATTERYSERVICE = '180f'
	TEMPSERVICE = '1809' 
	TYPEMANUDATA = 255
	TYPE16BSERVICEDATA = 22
	
class MinewScanHandler(object):
    def __init__(self, dev):
        self.servicedata = dev.getValueText(MinewUUIDS.TYPE16BSERVICEDATA)
	self.services = dev.serviceData
	self.addr    = dev.addr
	self.macid = self.addr.replace(":","")
	self.rssi  = dev.rssi

    def getS1Temp_old(self):
	rawTemp = self.servicedata[28:30] + self.servicedata[26:28]
	tempInt1 = int(rawTemp,16)
	tempInt2 = tempInt1 if tempInt1 < 0x7FFF else tempInt1 - 0x8000 - 0x8000 
	self.S1temp = tempInt2/10.0
	print rawTemp, self.S1temp
	return self.S1temp
    
    def getS1Humid_old(self):
	rawHumid = self.servicedata[32:34] + self.servicedata[30:32]
	humidInt1 = int(rawHumid,16)
	humidInt2 = humidInt1 if humidInt1 < 0x7FFF else humidInt1 - 0x8000  - 0x8000
	self.S1humid = humidInt2/10.0	
    	return self.S1humid
	
    def getS1Batt_old(self):
	self.S1batt   = int(self.servicedata[14:16],16)
	return self.S1batt

    def getS1Temp(self):
	rawTemp = self.servicedata[10:14]
	tempInt1 = int(rawTemp,16)
	tempInt2 = tempInt1 if tempInt1 < 0x7FFF else tempInt1 - 0x8000 - 0x8000 
	self.S1temp = round(tempInt2/256.0,2)
	print rawTemp, self.S1temp
	return self.S1temp
    
    def getS1Humid(self):
	rawHumid = self.servicedata[14:18]
	humidInt1 = int(rawHumid,16)
	humidInt2 = humidInt1 if humidInt1 < 0x7FFF else humidInt1 - 0x8000  - 0x8000
	self.S1humid = round(humidInt2/256.0,2)	
    	return self.S1humid
	
    def getS1Batt(self):
	self.S1batt   = int(self.servicedata[8:10],16)
	return self.S1batt



    def getBatt(self):
	self.doorSensorBatt =  int(self.services[MinewUUIDS.BATTERYSERVICE],16)
	return self.doorSensorBatt

    def getDoorStatus(self):
	self.doorStatus =  int(self.services[MinewUUIDS.DOORACTSERVICE],16)
	return self.doorStatus

    def getTemp(self):
	self.temp =  int(self.services[MinewUUIDS.TEMPSERVICE],16)
	return self.temp
		
    def getRssi(self):
	return self.rssi


    def pushToDB(self):
        
	nodeTS = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
	minewTempData  = [self.macid,self.getS1Temp(),nodeTS, self.getS1Batt(),self.getRssi()]
	minewHumidData = [self.macid,self.getS1Humid(),nodeTS,self.getS1Batt(),self.getRssi()]
#	print minewTempData
#	print minewHumidData
	try:
		con = sql.connect(bledb.PATHS.DB_PATH)
        	with con:
                	cur = con.cursor()
				
			cur.execute("""INSERT INTO TempData (NdId, \
			Temp,NdTs,NdBat,Ndrssi,upFlag) \
			values (?,?,?,?,?,0);""", minewTempData)
					
			cur.execute("""INSERT INTO HumData (NdId, \
			Hum,NdTs,NdBat,Ndrssi,upFlag) \
			values (?,?,?,?,?,0);""", minewHumidData)

			logger.info('MinewS1 temp data:%s', minewTempData)
			logger.info('MinewS1 humid data:%s', minewHumidData)
        	return True

	except Exception as ex:
		logger.exception("Exception pushing MinewS1 data to DB: %s",ex)
		return False

    def pushDoorActToDB(self):
        
	nodeTS = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
	DoorActData  = [self.macid,self.getDoorStatus(),nodeTS, self.getBatt(),self.getRssi()]
#	print DoorActData
	try:
		con = sql.connect(bledb.PATHS.DB_PATH)
        	with con:
                	cur = con.cursor()
				
			cur.execute("""INSERT INTO DoorActData (NdId, \
			DoorSts,NdTs,NdBat,NdRssi,upFlag) \
			values (?,?,?,?,?,0);""", DoorActData)
					
			logger.info('Door Activity data:%s', DoorActData)
        	return True

	except Exception as ex:
		logger.exception("Exception pushing MinewS1 data to DB: %s",ex)
		return False

