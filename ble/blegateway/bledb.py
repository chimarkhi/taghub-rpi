import time
import sqlite3 as sql
import requests
import datetime
import json
from collections import defaultdict
import logging

from gateway import Gateway, GatewayParams

class PATHS:
	DB_PATH = '/home/pi/tagbox/ble/blegateway/telemetryDB.db'
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
		NdBat REAL,
		upFlag INTEGER);""")
		
	# Humidity table

                cur.execute("""CREATE TABLE IF NOT EXISTS HumData 
                (seq INTEGER PRIMARY KEY AUTOINCREMENT, 
                NdId TEXT NOT NULL, 
                Hum REAL, 
                NdTs TEXT, 
		NdBat REAL,
		upFlag INTEGER);""")

	# Probe table

                cur.execute("""CREATE TABLE IF NOT EXISTS PrbData \
                (seq INTEGER PRIMARY KEY AUTOINCREMENT, \
                NdId TEXT NOT NULL, \
                Prb1 REAL, \
                Prb2 REAL, \
                NdTs TEXT, \
		NdBat REAL,
		upFlag INTEGER);""")
		
	# Door Activity  table

                cur.execute("""CREATE TABLE IF NOT EXISTS DoorActData 
                (seq INTEGER PRIMARY KEY AUTOINCREMENT, 
                NdId TEXT NOT NULL, 
                DoorStatus REAL, 
                NdTs TEXT, 
		NdBat REAL,
		upFlag INTEGER);""")

	
class dbQuorer():
	def __init__(self):
		self.con = sql.connect(PATHS.DB_PATH)
	
	def query_db(self,query, args=(), one=True):
        	cur = self.con.cursor()
        	cur.execute(query, args)
        	r = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        	cur.close()
        	return (r[0] if r else None) if one else r

	def getTableLen(self,table):
        	cur = self.con.cursor()
        	cur.execute("select count(*) from %s where upFlag == 0" %table)
		(tableLen,) = cur.fetchone()
		cur.close()
		return tableLen
	
	def readTable(self,table):
        	cur = self.con.cursor()
        	cur.execute("select *,min(seq) from %s where upFlag == 0" %table)
        	
		try:
			rawRow = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
			row    = {k:v for k,v in rawRow[0].items() if (k != 'seq' and k != 'upFlag' and k!='min(seq)')}		
			
		except Exception as ex:
			logging.info("Exception reading table entry %s", ex)
        	
		cur.close()
		return (rawRow[0]['seq'],row)

	def delRow(self,table,rowId):
        	cur = self.con.cursor()
        	cur.execute("delete from %s where seq = %s" %[table,rowId])
		cur.close()

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
  		cur = self.con.cursor()
		tables = cur.execute("select name from sqlite_master where type='table'")
		tables = tables.fetchall()
		tab=[name[0] for name in tables if (name[0] != 'sqlite_sequence'and name[0] != 'Payloads')]
		cur.close()
		return tab
	
	def packetToDB(self, data, Ts):
		try:		
			self.con.execute("insert into Payloads (Packet, PacketTs,upFlag) values(?,?,0)",[data,Ts])
		except Exception as ex:
			logging.error("Exception pushing payload to DB %s", ex)		
		self.con.commit()
		
	def updateRow(self,table,seq,value):
		try:
			self.con.execute("UPDATE %s SET upFlag = %s WHERE seq = %s;" %(table,value,seq))
		except Exception as ex:
			logging.erro('Exception setting upFlag %s', ex)
		self.con.commit()

	def close(self):
		self.con.close()


def createPacket():
		
	gw	 = Gateway()
	upPacket = gw.payload()
	dber = dbQuorer()
	
	data = defaultdict(dict)
	
	dataDBInfo = []
	payloadUnit = GatewayParams.MAX_PACKET_UNITS		

	while (len(json.dumps(upPacket)) < GatewayParams.PACKET_SIZE) and payloadUnit > 0:
		longestTable = dber.getPriority()
		(rowId, rowData) = dber.readTable(longestTable) 
		if rowId == None and payloadUnit == GatewayParams.MAX_PACKET_UNITS:
			logging.info('No data in any table')
			return False
		elif rowId != None:
			try:
				data[longestTable].append(rowData)
				dataDBInfo.append((longestTable,rowId))
			except AttributeError  :
				data[longestTable] =[]
				data[longestTable].append(rowData)
				dataDBInfo.append((longestTable,rowId))
			## set telemetry tables' rows' upFlag using info from dataDBInfo entries
			dber.updateRow(longestTable,rowId,'1')		
		payloadUnit -= 1
		upPacket.update({'Data':data})

	logging.info('Payload size %d', len(json.dumps(upPacket)))
	logging.info('Payload components %s', dataDBInfo)

	packetTs =  datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")		
	upPacketJson = json.dumps(upPacket)
	upPacketJsonPretty = json.dumps(upPacket,indent=4, sort_keys=True)
	dber.packetToDB(upPacketJson,packetTs)
	
	dber.close()

	logging.debug(upPacketJsonPretty)
		
	return True

def uploadPayload():
	upDone = 0
	dber = dbQuorer()
	
	(rowId, rowData) = dber.readTable('Payloads')
	payload = rowData['Packet']

	if rowId != None:
		try:
			r = requests.post(GatewayParams.DATA_LINK,data=payload, headers=GatewayParams.POST_HEADERS,timeout=GatewayParams.POST_TIMEOUT)
			if r != None:
				upDone = r.status_code
				if divmod(upDone,100)[0] == 2:						
					dber.updateRow('Payloads',rowId,str(upDone)) 	
					logging.info('Post request succesful with status : %d', upDone)
					dber.close()				
					return True
				else :
					logging.info('Post request UNsuccesful with status : %d', upDone)					
					dber.close()					
					return False
			else :
				logging.info('Payloads is empty')
				dber.close()
				return False
		except Exception as ex:
			logging.error( 'Payload POST request failed %s', ex)	
			dber.close()			
			return False
		



