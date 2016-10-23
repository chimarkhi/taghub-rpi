from apscheduler.schedulers.blocking import BlockingScheduler
import os
import bleadv
import bledb
import time
import datetime
import logging



## dir paths and file names
lib_path = '/home/pi/tagbox/ble/hci_testruns/' # scripts dir path
advDataFile = lib_path + 'ble_data_parsed.txt'
db_path = lib_path + 'blescanDB.db'



## Link to server lists
data_link='https://bliss-rdt.herokuapp.com/api/ble-data/'
device_link='https://bliss-rdt.herokuapp.com/api/ble-device/'
#data_link='http://139.59.3.212:8002/api/ble-data/'
#device_link='http://139.59.3.212:8002/api/ble-device/'


## Process parameters/variables
gatewayID = 4  # gateway/room ID as specified in server data lists	
passAll = True # Set true to ignore gatewayID and update/upload all scanned tags
printUpData = True # Set true for displaying the uploaded data


## Scheduling variables
refreshInterval = 6 # in hours
dBdelCycle = 2 # in days : dB deleted every dBdelcycle+1 days
whitelistDlInterval = 2 # in hours
scanInterval = 45 # in seconds : duration between each scan+parse+dbwrite process call
scanSleepTime = 20 # in seconds: unused 
uploadInterval = 5# in seconds : duration between each dbtoserver upload proceess call
bufferDays = 4 # in days : data older than bufferDays is deleted in 
scanTime = 12 # in seconds : duration for which ble devices are scanned each time parseAdv is called
postTimeout = 5 # in seconds : http post request timeout duration
getTimeout = 120 # in seconds : http get request timeout duration

## Misc initializations
datakeys = ()
scan_iterations = 10 # unused
i = 0		
Tag_List=[]
lastTime = datetime.datetime.now()
sched = BlockingScheduler()
logging.basicConfig()

@sched.scheduled_job('interval',hours = refreshInterval)
def RefreshProcess():
	currentTime = datetime.datetime.now()
	deltaTime = currentTime - lastTime
	if deltaTime.days > dBdelCycle:
		os.system('rm -rf '+ db_path)
		bledb.createDB(db_path,datakeys)


@sched.scheduled_job('interval',hours = whitelistDlInterval)
def WhitelistCreate():		
	## calling createDeviceList function to get ble_device list data
	
	Tag_List_new=bleadv.createDeviceList(device_link, getTimeout)
	if len(Tag_List_new) > 0:
		Tag_List = Tag_List_new
	else :
		for num in range(2,3):
			Tag_List_new=bleadv.createDeviceList(device_link, num*getTimeout)
		
	#data_fields=bleadv.createDeviceList(device_link)['data_fields']
	print 'No. of devices in whitelist are',len(Tag_List)
	return Tag_List		

@sched.scheduled_job('interval',seconds = scanInterval)
def ScanParseDB():
	## calling parseAdv to scan for ble devices, 
	## parse their adv packets and print out adv data
	## in ble_data_parsed.txt

	numTagsFound=bleadv.parseAdv(scanTime,lib_path,advDataFile)
	print('No. of advertisers scanned are: %d' %numTagsFound)
	
	## update temp, humidity and timestamp in Tag_List based on the adv data

	indexTagsUp=bleadv.tagDataUpdate(Tag_List,advDataFile,gatewayID,passAll)
	print('No. of tags updated are: %d' %len(indexTagsUp))

	
	## Inefficient : tag info converted from object to list (tagData)

	for i in indexTagsUp:
		tagData=[i.macid,i.name,i.temp,i.humidity,i.timestamp,i.gateway,i.batt]
		bledb.pushDB(db_path,tagData,datakeys,bufferDays)
		
	
	#time.sleep(scanSleepTime)


@sched.scheduled_job('interval',seconds = uploadInterval)
def DBtoServer():
	upDone=bledb.popDB(db_path,data_link,bufferDays,postTimeout)
	print upDone

	#time.sleep(sleeptime)


bledb.createDB(db_path,datakeys)
RefreshProcess()
Tag_List = WhitelistCreate()
ScanParseDB()

sched.start()
