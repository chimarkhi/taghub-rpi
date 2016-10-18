from apscheduler.schedulers.blocking import BlockingScheduler
from twilio.rest import TwilioRestClient
import os
import bleadv
import bledb
import time
import datetime
import logging


## Twilio Setup
ACCOUNT_SID = "AC23220de1bcd087dcfd7c07711f4d6847" 
AUTH_TOKEN = "bdb845bced15060a6dcfe74bc71b8593"  
twilioClient = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN) 
toPhone_sameer = "+919620647577"
toPhone_adarsh = "+919535964140"
toPhone_somesh = "+919740612610"
toPhone_saumitra = "+919845660136"
fromPhone = "+12568575110"


## Link to server lists
#data_link='https://bliss-rdt.herokuapp.com/api/ble-data/'
#device_link='https://bliss-rdt.herokuapp.com/api/ble-device/'
data_link='http://139.59.3.212:8002/api/ble-data/'
device_link='http://139.59.3.212:8002/api/ble-device/'


## Process parameters/variables
gatewayID = 4  # gateway/room ID as specified in server data lists	
passAll = True # Set true to ignore gatewayID and update/upload all scanned tags
printUpData = True # Set true for displaying the uploaded data


## Scheduling variables
alertCycleDelay = 120 # in seconds : sleep delay in alerts loop
refreshInterval = 6 # in hours
dBdelCycle = 2 # in days : dB deleted every dBdelcycle+1 days
whitelistDlInterval = 2 # in hours
scanInterval = 150 # in seconds : duration between each scan+parse+dbwrite process call
scanSleepTime = 20 # in seconds: unused 
uploadInterval = 3# in seconds : duration between each dbtoserver upload proceess call
bufferDays = 4 # in days : data older than bufferDays is deleted in 
scanTime = 12 # in seconds : duration for which ble devices are scanned each time parseAdv is called
postTimeout = 1 # in seconds : http post request timeout duration
getTimeout = 120 # in seconds : http get request timeout duration
downTimeLimit = 1200 # in seconds : no fresh data time duration exceeding which alert is sent 

## Misc initializations
Tag_List=[]
smsCount = 0

def sendAlert(alertBody, targetPhone):
	twilioClient.messages.create(
		to=targetPhone, 
		from_=fromPhone, 
		body=alertBody,  
	) 


def dataAlerts():		
	## calling createDeviceList function to get ble_device list data

	Tag_List=bleadv.createDeviceList(device_link, getTimeout)
	
	global smsCount
	timeSinceAllTags=[]
	secSinceAllTags=[]
	
	for i in Tag_List :
		
		ts = i.modifiedOn
		lastupdate = datetime.datetime(int(ts[0:4]),int(ts[5:7]),int(ts[8:10]),int(ts[11:13]),int(ts[14:16]),int(ts[17:19]),int(ts[20:26]))
		timenow = datetime.datetime.now()
		timeSince = timenow - lastupdate
		timeSinceAllTags.append(timeSince)
		secSinceAllTags.append(timeSince.total_seconds())
		
	if max(secSinceAllTags) > downTimeLimit:
		if smsCount < 3:
			sendAlert("No data uploaded in last "+str(min(timeSinceAllTags))+" hours",toPhone_sameer)
			sendAlert("No data uploaded in last "+str(min(timeSinceAllTags))+" hours",toPhone_adarsh)
			sendAlert("No data uploaded in last "+str(min(timeSinceAllTags))+" hours",toPhone_saumitra)

			print("No data uploaded in last "+str(min(timeSinceAllTags))+ " hours")
			smsCount = smsCount + 1
			print(smsCount)
			
	elif max(secSinceAllTags) < downTimeLimit:
		if smsCount > 0:
			print("Data upload resumed; smsCount:%d",smsCount)
			sendAlert("Data upload resumed",toPhone_sameer)
			sendAlert("Data upload resumed",toPhone_adarsh)
			sendAlert("Data upload resumed",toPhone_saumitra)		
		smsCount = 0	

	print 'Number of devices in whitelist are',len(Tag_List)


	
while(1):
	Tag_List = dataAlerts()
	time.sleep(alertCycleDelay)
