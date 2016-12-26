import time
import sqlite3 as sql
import requests
import datetime

## datakeys is a tuple: (device, tagname, temp, humidity, tstamp, gateway)
## database log
def createDB(db_path,datakeys):
	con = sql.connect(db_path)
	
	with con:
		cur = con.cursor()
		cur.execute("""CREATE TABLE IF NOT EXISTS uploadFIFO \
		(id INTEGER PRIMARY KEY AUTOINCREMENT, \
		device TEXT NOT NULL, \
		tagname TEXT NOT NULL, \
		temp REAL, \
		humidity REAL, \
		device_timestamp TEXT, \
		gateway INTEGER,
		batt REAL);""")

                cur.execute("""CREATE TABLE IF NOT EXISTS localData \
                (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                device TEXT NOT NULL, \
                tagname TEXT NOT NULL, \
                temp REAL, \
       	        humidity REAL, \
                device_timestamp TEXT, \
       	        gateway INTEGER, \
		batt REAL,
		logdate TEXT, \
		logtime TEXT,
		uploadFlag INTEGER);""")
		
		
	
def pushDB(db_path, tagData, datakeys, bufferDays):
        con = sql.connect(db_path)

        with con:
                cur = con.cursor()
		
		cur.execute("""INSERT INTO uploadFIFO (device,tagname, \
		temp,humidity,device_timestamp,gateway,batt) \
		values (?,?,?,?,?,?,?);""", tagData)
		
		cur.execute("""INSERT INTO localData (device,tagname, \
		temp,humidity,device_timestamp,gateway,batt,logdate,logtime,uploadFlag) \
		values (?,?,?,?,?,?,?,DATE('now'),TIME('now'),0);""", tagData)
		


def popDB(db_path,data_link,bufferDays,postTimeout,postHeaders):
	class TagInfo:
		pass
	
	tag = TagInfo()	
	upDone = 0
	
	con = sql.connect(db_path)
	with con:
		cur=con.cursor()
		cur.execute("SELECT *,MIN(id) FROM uploadFIFO;")
		roi=cur.fetchone()
		print roi
		min_index = roi[0]
		tag.macid = roi[1]
		tag.name = roi[2]
		tag.notified = False
		tag.gateway = roi[6]
		tag.environment = 0
		tag.humidity = roi[4]
		tag.temp = roi[3]
		tag.batt = roi[7]
		tag.timestamp = roi[5]
		
		payload = {"device":str(roi[1]),
			"device_datetime":str(roi[5]),
			"humidity":roi[4],
			"temperature":roi[3]}
		
		if roi[0]:
			try:
				r=requests.post(data_link,json=payload,headers=postHeaders,timeout=postTimeout)			

				try:
					upDone = r.status_code
				except:
					upDone = 2
			except:
				upDone = 0
			finally:
				try:
					if divmod(upDone,100)[0] == 2:						
						con.execute("DELETE FROM uploadFIFO WHERE id = {mi};" .format(mi=min_index))	
				except:
					pass

			## Update the upDone flag of recently uploaded data point in localData table	
			cur.execute("UPDATE localData SET uploadFlag={ud} \
			WHERE id = {mi};".format(ud=upDone,mi=min_index))

		else:	
			print "No data left in FIFO"
			
		
		
		## Delete old data in localData table
		con.execute("DELETE FROM localData WHERE DATE('now')-logdate>={bd};"\
		.format(bd=bufferDays))
		
	return upDone


def popDBforAzure(gatewayID,db_path,data_link,bufferDays,postTimeout,postHeaders):
	class TagInfo:
		pass
	
	tag = TagInfo()	
	upDone = 0
	
	con = sql.connect(db_path)
	with con:
		cur=con.cursor()
		cur.execute("SELECT *,MIN(id) FROM uploadFIFO;")
		roi=cur.fetchone()
		print roi
		min_index = roi[0]
		tag.macid = roi[1]
		tag.name = roi[2]
		tag.notified = False
		tag.gateway = roi[6]
		tag.environment = 0
		tag.humidity = roi[4]
		tag.temp = roi[3]
		tag.batt = roi[7]
		tag.timestamp = roi[5]
		
		payload = {
			"GwId":gatewayID,
			"GwTs":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
			"Data":{
			"TempData":[
			{
			"NdId":str(roi[1]),
			"Temp":str(roi[3]),
			"NdTs":str(roi[5])
			}
			],
			"HumData":[
			{
			"NdId":str(roi[1]),
			"Hum":str(roi[4]),
			"NdTs":str(roi[5])
			}
			]
			}
			}
		
		if roi[0]:
			try:
				r=requests.post(data_link,json=payload,headers=postHeaders,timeout=postTimeout)			

				try:
					upDone = r.status_code
				except:
					upDone = 2
			except:
				upDone = 0
			finally:
				try:
					if divmod(upDone,100)[0] == 2:
						con.execute("DELETE FROM uploadFIFO WHERE id = {mi};" .format(mi=min_index))	
				except:
					pass

			## Update the upDone flag of recently uploaded data point in localData table	
			cur.execute("UPDATE localData SET uploadFlag={ud} \
			WHERE id = {mi};".format(ud=upDone,mi=min_index))

		else:	
			print "No data left in FIFO"
			
		
		
		## Delete old data in localData table
		con.execute("DELETE FROM localData WHERE logdate<DATE('now', '-{bd} days');"\
		.format(bd=bufferDays))
		
	return upDone

