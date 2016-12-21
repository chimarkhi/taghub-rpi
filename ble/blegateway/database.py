import time
import sqlite3 as sql
import requests
import datetime
import json


class PATHS:
	db_path = '/home/pi/tagbox/ble/cappec/telemetryDB.db'
## Create table if not already present 
## 
def createDB():
	con = sql.connect(PATHS.db_path)
	
	with con:
		cur = con.cursor()
	
	# Temp table	
		cur.execute("""CREATE TABLE IF NOT EXISTS tempFIFO \
		(id INTEGER PRIMARY KEY AUTOINCREMENT, \
		device TEXT NOT NULL, \
		temp REAL, \
		device_timestamp TEXT, \
		gateway TEXT NOT NULL,
		batt REAL);""")

                cur.execute("""CREATE TABLE IF NOT EXISTS tempHist \
                (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                device TEXT NOT NULL, \
                temp REAL, \
                device_timestamp TEXT, \
		gateway TEXT NOT NULL,
		batt REAL,
		uploadFlag INTEGER);""")
		

	# Humidity table
		cur.execute("""CREATE TABLE IF NOT EXISTS humidFIFO \
		(id INTEGER PRIMARY KEY AUTOINCREMENT, \
		device TEXT NOT NULL, \
		humid REAL, \
		device_timestamp TEXT, \
		gateway TEXT NOT NULL,
		batt REAL);""")

                cur.execute("""CREATE TABLE IF NOT EXISTS humidHist \
                (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                device TEXT NOT NULL, \
                humid REAL, \
                device_timestamp TEXT, \
		gateway TEXT NOT NULL,
		batt REAL,
		uploadFlag INTEGER);""")
		

	# Probe table
		cur.execute("""CREATE TABLE IF NOT EXISTS probeFIFO \
		(id INTEGER PRIMARY KEY AUTOINCREMENT, \
		device TEXT NOT NULL, \
		probeOneTemp REAL, \
		probeTwoTemp REAL, \
		device_timestamp TEXT, \
		gateway TEXT NOT NULL,
		batt REAL);""")

                cur.execute("""CREATE TABLE IF NOT EXISTS probeHist \
                (id INTEGER PRIMARY KEY AUTOINCREMENT, \
                device TEXT NOT NULL, \
                probeOneTemp REAL, \
                probeTwoTemp REAL, \
                device_timestamp TEXT, \
		gateway TEXT NOT NULL,
		batt REAL,
		uploadFlag INTEGER);""")
		
class DBEntry(object):
	def __init__(self, db_name):
		
	
