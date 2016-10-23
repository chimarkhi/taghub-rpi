import time
import datetime
import requests
import os
import bleadv
import bledb

## Variables
db_path = "blescanDB.db"
datakeys = ()
scan_iterations=10 # unused
i=0		
lib_path="/home/pi/tagbox/ble/hci_testruns/" # dir path
scantime=10 #scan duration in secs
sleeptime=120 # sleep duration in secs
gatewayID=4  # gateway/room ID as specified in server data lists	
bufferDays=2
passAll=True # Set true to ignore gatewayID and update/upload all scanned tags
printUpData=True # Set true for displaying the uploaded data

## temp file names
advDataFile='./ble_data_parsed.txt'

## Link to lists in cloud
data_link='https://bliss-rdt.herokuapp.com/api/ble-data/'
device_link='https://bliss-rdt.herokuapp.com/api/ble-device/'

## calling createDeviceList function to get ble_device list data
Tag_List=bleadv.createDeviceList(device_link)
#data_fields=bleadv.createDeviceList(device_link)['data_fields']

print 'No. of devices in whitelist are',len(Tag_List)
#print 'Keys in whitelist:',data_fields


## create database with 2 tables only if one of the same name doesnt exist before
## 1. uploadFIFO : contains only data that hasnt been uploaded yet
## 2. localData : contains all adv packets read by the gateway 
bledb.createDB(db_path,datakeys)

while (1):

	## calling parseAdv to scan for ble devices, 
	## parse their adv packets and print out adv data
	## in ble_data_parsed.txt
	
	numTagsFound=bleadv.parseAdv(scantime,lib_path,advDataFile)
	print('No. of advertisers scanned are: %d' %numTagsFound)

	
	## update temp, humidity and timestamp in Tag_List based on the adv data
	
	indexTagsUp=bleadv.tagDataUpdate(Tag_List,advDataFile,gatewayID,passAll)
	print('No. of tags updated are: %d' %len(indexTagsUp))
	
 	
	## Inefficient : tag info converted from object to list (tagData)
	
	for i in indexTagsUp:
		tagData=[i.macid,i.name,i.temp,i.humidity,i.timestamp,i.gateway,i.batt]
		bledb.pushDB(db_path,tagData,datakeys,bufferDays)
			
		
	time.sleep(sleeptime)


## A parallel process to upload data from db to server called from a
## a different python file : dbtoserver.py

		
