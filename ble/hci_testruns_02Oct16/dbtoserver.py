import time
import datetime
import requests
import os
import bleadv
import bledb

## process that routinely (check sleeptime) uploads a single unit of 
## data from db to server

## Variables
db_path = "blescanDB.db"
datakeys = ()
scan_iterations=10 # unused
i=0		
lib_path="/home/pi/tagbox/ble/hci_testruns/" # dir path
scantime=10 #scan duration in secs
sleeptime=10 # sleep duration in secs
gatewayID=4  # gateway/room ID as specified in server data lists	
bufferDays=2
passAll=True # Set true to ignore gatewayID and update/upload all scanned tags
printUpData=True # Set true for displaying the uploaded data

## temp file names
advDataFile='./ble_data_parsed.txt'

## Link to lists in cloud
data_link='https://bliss-rdt.herokuapp.com/api/ble-data/'
device_link='https://bliss-rdt.herokuapp.com/api/ble-device/'

while(1):
	upDone=bledb.popDB(db_path,data_link,bufferDays)
	print upDone
	
	time.sleep(sleeptime)
