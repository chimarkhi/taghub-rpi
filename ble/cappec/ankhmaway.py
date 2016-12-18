import bluepy.btle as btle
import time
import datetime
import sqlite3 as sql
import logging

import bledb

class UUIDS:
	TEMP_SERVICE 	= btle.UUID("fe551580-4180-8a02-ef2c-1b42a0ac3f83")
	TEMP_CHAR	= btle.UUID("fe551582-4180-8a02-ef2c-1b42a0ac3f83")	
	TYPEMANUDATA	= 255
	
class AMScanHandler(object):
    def __init__(self, dev):
        self.advdata = dev.getValueText(UUIDS.TYPEMANUDATA)
	self.addr    = dev.addr
	self.majorID = self.advdata[40:44]
	self.minorID = self.advdata[44:48]

    def getTemp(self):
	temp_hex    = hex(((int(self.majorID,16)&0x00ff)<<8)^((int(self.minorID,16)&0xc000)>>8))
	temp1       = int(temp_hex,16)
	self.temp   = round(((175.52*temp1/(2**16))-46.85),2)
	return self.temp
    
    def getHumid(self):
	humid_hex   = hex(int(self.majorID,16)&0xff00)
	humid1      = int(humid_hex,16)
	self.humid  = round(((125*humid1/(2**16))-6),2)
    	return self.humid
	
    def getBatt(self):
	self.batt   = round((int(hex((int(self.minorID,16)&0xF000)>>8),16)*16.0/100),2)
	return self.batt
		
    def pushToDB(self):
        
	nodeTS = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
	amTempData  = [self.addr,self.getTemp(),nodeTS, self.getBatt()]
	amHumidData = [self.addr,self.getHumid(),nodeTS,self.getBatt()]
		
	try:
		con = sql.connect(bledb.PATHS.DB_PATH)
        	with con:
                	cur = con.cursor()
				
			cur.execute("""INSERT INTO TempData (NdId, \
			Temp,NdTs,NdBat,upFlag) \
			values (?,?,?,?,0);""", amTempData)
					
			cur.execute("""INSERT INTO HumidData (NdId, \
			Hum,NdTs,NdBat,upFlag) \
			values (?,?,?,?,0);""", amHumidData)

			logging.info('AM temp data:%s', amTempData)
			logging.info('AM humid data:%s', amHumidData)
        	return True

	except Exception as ex:
		logging.error("Exception pushing AM data to DB: ",ex)
		return False


