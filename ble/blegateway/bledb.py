import time
import sqlite3 as sql
import requests
import datetime
import json
from collections import defaultdict
import logging

from gateway import Gateway, GatewayParamsStatic
import GatewayParams
import mqttClient

logger = logging.getLogger(__name__)

class PATHS:
	DB_PATH = '/home/pi/tagbox/ble/blegateway/telemetryDB'+GatewayParamsStatic.NAME+'.db'
## Create table if not already present 
## 
def createDB():
	con = sql.connect(PATHS.DB_PATH)
	
	with con:
		cur = con.cursor()

	# Formed Data Packets table	

                cur.execute("""CREATE TABLE IF NOT EXISTS Payloads 
                (seq INTEGER PRIMARY KEY AUTOINCREMENT, 
                Packet TEXT NOT NULL, 
		PacketTs REAL,
		upFlag INTEGER);""")
	
	# Temp table	

                cur.execute("""CREATE TABLE IF NOT EXISTS TempData 
                (seq INTEGER PRIMARY KEY AUTOINCREMENT, 
                NdId TEXT NOT NULL, 
                Temp REAL, 
                NdTs TEXT, 
		NdBat INTEGER,
		upFlag INTEGER);""")
		
	# Humidity table

                cur.execute("""CREATE TABLE IF NOT EXISTS HumData 
                (seq INTEGER PRIMARY KEY AUTOINCREMENT, 
                NdId TEXT NOT NULL, 
                Hum REAL, 
                NdTs TEXT, 
		NdBat INTEGER,
		upFlag INTEGER);""")

	# Probe table

                cur.execute("""CREATE TABLE IF NOT EXISTS PrbData \
                (seq INTEGER PRIMARY KEY AUTOINCREMENT, \
                NdId TEXT NOT NULL, \
                Prb1 REAL, \
                Prb2 REAL, \
                NdTs TEXT, \
		NdBat INTEGER,
		upFlag INTEGER);""")
		
	# Door Activity  table

                cur.execute("""CREATE TABLE IF NOT EXISTS DoorActData 
                (seq INTEGER PRIMARY KEY AUTOINCREMENT, 
                NdId TEXT NOT NULL, 
                DoorSts INTEGER, 
                NdTs TEXT, 
		NdBat INTEGER,
		upFlag INTEGER);""")

	# Energy Meter readings  table

                cur.execute("""CREATE TABLE IF NOT EXISTS NrgData 
                (seq INTEGER PRIMARY KEY AUTOINCREMENT, 
                NdId TEXT NOT NULL, 
                VoltRN REAL, 
		CurrR REAL,
		PfR REAL,
		AppPwrR REAL,
		ActNrg REAL,
                NdTs TEXT, 
		NdBat INTEGER,
		upFlag INTEGER);""")

	
class dbQuorer():
	def __init__(self):
		self.con = sql.connect(PATHS.DB_PATH)
	
	def query_db(self,query, args=(), one=True):
        	with self.con:
			cur = cself.con.cursor()
        		cur.execute(query, args)
     		   	r = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        	return (r[0] if r else None) if one else r

	def getTableLen(self,table):
        	with self.con :
			cur = self.con.cursor()
        		cur.execute("select count(*) from %s where upFlag == 0" %table)
			(tableLen,) = cur.fetchone()
		return tableLen
	
	def readTable(self,table):
        	with self.con :
			cur = self.con.cursor()
        		cur.execute("select *,min(seq) from %s where upFlag == 0" %table)
        	
			try:
				rawRow = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
				row    = {k:v for k,v in rawRow[0].items() if (k != 'seq' and k != 'upFlag' and k!='min(seq)')}		
			
			except Exception as ex:
				logger.info("Exception reading table entry %s", ex)

		return (rawRow[0]['seq'],row)

	def delRow(self,table,rowId):
        	with self.con :
			cur = self.con.cursor()
        		cur.execute("delete from %s where seq = %s" %[table,rowId])
		
	def delOldRows(self,table,keepDays):
		if table == 'Payloads':
			self.con.execute("delete from %s where PacketTs<DATE('now', '- %s days');"  %(table,keepDays)) 
#			self.con.execute('select @@rowcount as deleted;')
		else :
			self.con.execute("delete from %s where NdTs<DATE('now', '- %s days');"  %(table,keepDays)) 
#			self.con.execute('select @@rowcount as deleted;')
		self.con.commit()
			
	def getPriority(self):
		tab = self.getTableNames()
		priority = tab[0]
		seq = []	
		for name in tab:
			seq.append(self.getTableLen(name))
			if seq[-1] == max(seq):
				priority = name
		return priority
	
	def getTableNames(self):
  		with self.con:
			cur = self.con.cursor()
			tables = cur.execute("select name from sqlite_master where type='table'")
			tables = tables.fetchall()
			tab=[name[0] for name in tables if (name[0] != 'sqlite_sequence'and name[0] != 'Payloads')]
		return tab
	
	def packetToDB(self, data, Ts):
		try:		
			self.con.execute("insert into Payloads (Packet, PacketTs,upFlag) values(?,?,0)",[data,Ts])
			self.con.commit()
		except Exception as ex:
			logger.exception("Exception pushing payload to DB %s", ex)		
		self.con.commit()
		
	def updateRow(self,table,seq,value):
		try:
			self.con.execute("UPDATE %s SET upFlag = %s WHERE seq = %s;" %(table,value,seq))
		except Exception as ex:
			logger.exception('Exception setting upFlag %s', ex)
		self.con.commit()

	def close(self):
		self.con.close()


def createPacket():
		
	gw	 = Gateway()
	upPacket = gw.payload()
	dber = dbQuorer()
	
	data = defaultdict(dict)
	tables = dber.getTableNames()
	dataDBInfo = []
	payloadUnit = GatewayParams.MAX_PACKET_UNITS		
	
	
	while (len(json.dumps(upPacket)) < GatewayParams.PACKET_SIZE) and payloadUnit > 0:
#		tab = dber.getPriority()
#		(rowId, rowData) = dber.readTable(tab) 
		for tab in tables:
			(rowId, rowData) = dber.readTable(tab)
			if rowId == None :
				tables.remove(tab)
				if len(tables) == 0 :
					logger.info('All data from all tables copied to Payloads table')
					break
			elif rowId != None:
				try:
					data[tab].append(rowData)
					dataDBInfo.append((tab,rowId))
				except AttributeError  :
					data[tab] =[]
					data[tab].append(rowData)
					dataDBInfo.append((tab,rowId))
				## set telemetry tables' rows' upFlag using info from dataDBInfo entries
				dber.updateRow(tab,rowId,'1')		
				payloadUnit -= 1
			upPacket.update({'Data':data})
		else :
			continue
		break
	
	if len(data) == 0:
		logger.info('No data in any table')
		return GatewayParams.PACKET_SIZE - payloadUnit
		dber.close()
	else:
		logger.info('Payload size %d', len(json.dumps(upPacket)))
		logger.info('Payload components %s', dataDBInfo)

		packetTs =  datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")		
		upPacketJson = json.dumps(upPacket)
		upPacketJsonPretty = json.dumps(upPacket,indent=4, sort_keys=True)
		dber.packetToDB(upPacketJson,packetTs)

		dber.close()

		logger.debug(upPacketJsonPretty)
		return GatewayParams.PACKET_SIZE - payloadUnit
		

def uploadPayload():
	upDone = 0
	dber = dbQuorer()
	
	(rowId, rowData) = dber.readTable('Payloads')
	payload = rowData['Packet']

	if rowId != None:
		try:
			if GatewayParams.COMMTYPE == "HTTPS" :			
				r = requests.post(GatewayParamsStatic.DATA_LINK,data=payload, headers=GatewayParamsStatic.POST_HEADERS,timeout=GatewayParams.POST_TIMEOUT)
			elif GatewayParams.COMMTYPE == "MQTT" :
				mqtter = mqttClient.MQTTClient("azure")
				(r,mid) = mqtter.pubSingle(payload)
			if r != None and GatewayParams.COMMTYPE == "HTTPS" :
				upDone = r.status_code
				if divmod(upDone,100)[0] == 2:						
					dber.updateRow('Payloads',rowId,str(upDone)) 	
					logger.info('Post request successful with status : %d', upDone)
					dber.close()				
					return True
				else :
					logger.info('Post request UNsuccessful with status : %d', upDone)					
					dber.close()					
					return False
			elif r != None and GatewayParams.COMMTYPE == "MQTT":
				upDone = r
				if upDone == 0:						
					dber.updateRow('Payloads', rowId, str(upDone)) 	
					logger.info('Post request successful with status : %d', upDone)
					dber.close()				
					return True
				else :
					logger.info('Post request  UNsuccessful with status : %d', upDone)					
					dber.close()					
					return False
			elif r == None  :
				logger.info('Post request on HTTPS/MQTT returned a NULL status code')
				dber.close()
				return False
		except Exception as ex:
			logger.exception( 'Payload POST request failed %s', ex)	
			dber.close()			
			return False
	else :
		logger.info('Payloads is empty')
		dber.close()
		return False
	



