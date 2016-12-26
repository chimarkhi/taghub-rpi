import bluepy.btle as btle
import time
import datetime
import sqlite3 as sql
import logging

import bledb

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

    def getS1Temp(self):
	rawTemp = self.servicedata[28:30] + self.servicedata[26:28]
	tempInt1 = int(rawTemp,16)
	tempInt2 = tempInt1 if tempInt1 < 0x7FFF else tempInt1 - 0x8000  
	self.S1temp = tempInt2/10.0
	return self.S1temp
    
    def getS1Humid(self):
	rawHumid = self.servicedata[32:34] + self.servicedata[30:32]
	humidInt1 = int(rawHumid,16)
	humidInt2 = humidInt1 if humidInt1 < 0x7FFF else humidInt1 - 0x8000  
	self.S1humid = humidInt2/10.0	
    	return self.S1humid
	
    def getS1Batt(self):
	self.S1batt   = int(self.servicedata[14:16],16)
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
		
    def pushToDB(self):
        
	nodeTS = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
	minewTempData  = [self.addr,self.getS1Temp(),nodeTS, self.getS1Batt()]
	minewHumidData = [self.addr,self.getS1Humid(),nodeTS,self.getS1Batt()]
#	print minewTempData
#	print minewHumidData
	try:
		con = sql.connect(bledb.PATHS.DB_PATH)
        	with con:
                	cur = con.cursor()
				
			cur.execute("""INSERT INTO TempData (NdId, \
			Temp,NdTs,NdBat,upFlag) \
			values (?,?,?,?,0);""", minewTempData)
					
			cur.execute("""INSERT INTO HumData (NdId, \
			Hum,NdTs,NdBat,upFlag) \
			values (?,?,?,?,0);""", minewHumidData)

			logging.info('MinewS1 temp data:%s', minewTempData)
			logging.info('MinewS1 humid data:%s', minewHumidData)
        	return True

	except Exception as ex:
		logging.error("Exception pushing MinewS1 data to DB: ",ex)
		return False

    def pushDoorActToDB(self):
        
	nodeTS = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
	DoorActData  = [self.addr,self.getDoorStatus(),nodeTS, self.getBatt()]
#	print DoorActData
	try:
		con = sql.connect(bledb.PATHS.DB_PATH)
        	with con:
                	cur = con.cursor()
				
			cur.execute("""INSERT INTO DoorActData (NdId, \
			DoorStatus,NdTs,NdBat,upFlag) \
			values (?,?,?,?,0);""", DoorActData)
					
			logging.info('Door Activity data:%s', DoorActData)
        	return True

	except Exception as ex:
		logging.error("Exception pushing MinewS1 data to DB: ",ex)
		return False

