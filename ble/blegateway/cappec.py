import bluepy.btle as btle
import time
import datetime
import sqlite3 as sql
import logging

import bledb

logger = logging.getLogger(__name__)

class UUIDS:
	TEMP_SERVICE 	= btle.UUID("fe551580-4180-8a02-ef2c-1b42a0ac3f83")
	TEMP_CHAR	= btle.UUID("fe551582-4180-8a02-ef2c-1b42a0ac3f83")	
	


class CappecPeripheral(btle.Peripheral):

    def __init__(self, dev):
        """
        Connects to the device given by address performing necessary authentication
        """
    	btle.Peripheral.__init__(self, dev.addr,addrType=btle.ADDR_TYPE_RANDOM)
	self.addr = dev.addr
	self.macid = self.addr.replace(":","")

	
    def characteristic(self, uuid):
        """
        Returns the characteristic for a given uuid.
        """
        self.characteristics = self.getCharacteristics()
	
	for c in self.characteristics:
            if c.uuid == uuid:
                return c


    def getProbeTemp(self):
        # find characteristics for battery and temperature

        self.temp_char = self.characteristic(UUIDS.TEMP_CHAR)
	
	temp_data = self.temp_char.read()
	tempProbeOne = None if ord(temp_data[0]) == 255 else round(((ord(temp_data[0])-32)*5.0/9),2) 
	tempProbeTwo = None if ord(temp_data[2]) == 255 else round(((ord(temp_data[2])-32)*5.0/9),2) 

        return [tempProbeOne, tempProbeTwo]
	

    def pushToDB(self):
        
	nodeTS = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
	probeData = [self.macid,self.getProbeTemp()[0],self.getProbeTemp()[1],nodeTS,None]
	
	
	try:
		con = sql.connect(bledb.PATHS.DB_PATH)
        	with con:
                	cur = con.cursor()
		
			cur.execute("""INSERT INTO PrbData (NdId, \
			Prb1,Prb2,NdTs,NdBat,upFlag) \
			values (?,?,?,?,?,0);""", probeData)
		
			logger.info('Probe temp readings : %s',probeData)
			
        	return True

	except Exception as ex:
		logger.exception("Error pushing probeData to DB: %s",ex)
		return False


