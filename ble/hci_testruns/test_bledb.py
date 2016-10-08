import time
import datetime
import sqlite3 as sql
import bledb
import os


db_path = "/home/pi/tagbox/sqlite/testDB.db"
datakeys = ()
gatewayID = 4
batt = 95
bufferDays=2

## Link to lists in cloud
data_link='https://bliss-rdt.herokuapp.com/api/ble-data/'
device_link='https://bliss-rdt.herokuapp.com/api/ble-device/'

# device,tagname,temp,humidity,tstamp,gateway
tagData=("FFFF0000","Tag001",-15.0,47.5,datetime.datetime.now(),gatewayID,batt)

os.system("cd ~/tagbox/ble/hci_testruns/")
#os.system("rm -rf testDB.db")
bledb.createDB(db_path,datakeys)
bledb.pushDB(db_path, tagData, datakeys,bufferDays)

TagInfo=bledb.popDB(db_path,data_link,bufferDays)
print TagInfo.macid, TagInfo.temp, TagInfo.timestamp
