import time
import sqlite3 as sql


## datakeys is a tuple: (macid, dev_name, temp, humidity, tstamp, gateway)
## database log
def createDB(db_path,datakeys):
	con = sql.connect("db_path")
	
	with con:
		cur = con.cursor()
		cur.execute("""CREATE TABLE IF NOT EXISTS uploadFIFO \
		(ID INT PRIMARY KEY AUTOINCREMENT, \
		datakeys[0] TEXT NOT NULL, \
		datakeys[1] TEXT NOT NULL, \
		datakeys[2] REAL, \
		datakeys[3] REAL, \
		datakeys[4] TEXT, \
		datakeys[5] INTEGER, \
		tstamp DATETIME NOT NULL);""")

                cur.execute("""CREATE TABLE IF NOT EXISTS localData \
                (ID INT PRIMARY KEY AUTOINCREMENT, \
                datakeys[0] TEXT NOT NULL, \
                datakeys[1] TEXT NOT NULL, \
                datakeys[2] REAL, \
       	        datakeys[3] REAL, \
                datakeys[4] TEXT, \
       	        datakeys[5] INTEGER);""")

def updateDB(db_path, tagData, datakeys)
        con = sql.connect("db_path")
	now = datetime.datetime.now()
        with con:
                cur = con.cursor()
		cur.execute("""INSERT INTO uploadFIFO (macid,name,temp,humidity,tstamp,gateway) \
		values (?,?,?,?,?,?)""",tagData)
	
