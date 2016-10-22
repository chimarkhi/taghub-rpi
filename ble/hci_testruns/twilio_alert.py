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
#toPhone = "+919620647577"
toPhone = "+919535964140"
#toPhone = "+919740612610"
fromPhone = "+12568575110"


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
alertCycleDelay = 10 # in seconds : sleep delay in alerts loop
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

## Misc initializations
Tag_List=[]

def sendAlert(alertBody):
	twilioClient.messages.create(
		to=toPhone, 
		from_=fromPhone, 
		body=alertBody,  
	) 


def deviceAlerts():		
	## calling createDeviceList function to get ble_device list data
	
	Tag_List=bleadv.createDeviceList(device_link, getTimeout)
	
	for i in Tag_List :
		if i.environment == 3 :
			if i.temp > 29:
				sendAlert("Upper limit breached: Temperature of "+i.name+ " is " +str(i.temp))
				print("Upper limit breached: Temperature of "+i.name+ " is " +str(i.temp))
			elif i.temp < 18:
				sendAlert("Lower limit breached: Temperature of "+i.name+ " is " +str(i.temp))
				print("Upper limit breached: Temperature of "+i.name+ " is " +str(i.temp))	
		elif i.environment == 2 :
			if i.temp > 11:
				sendAlert("Upper limit breached: Temperature of "+i.name+ " is " +str(i.temp))
				print("Upper limit breached: Temperature of "+i.name+ " is " +str(i.temp))
			elif i.temp < -10:
				sendAlert("Lower limit breached: Temperature of "+i.name+ " is " +str(i.temp))
				print("Upper limit breached: Temperature of "+i.name+ " is " +str(i.temp))
		elif i.environment == 1 :
			if i.temp > 60:
				sendAlert("Upper limit breached: Temperature of "+i.name+ " is " +str(i.temp))
				print("Upper limit breached: Temperature of "+i.name+ " is " +str(i.temp))
			elif i.temp < 0:
				sendAlert("Lower limit breached: Temperature of "+i.name+ " is " +str(i.temp))
				print("Upper limit breached: Temperature of "+i.name+ " is " +str(i.temp))
		else :
			print(i.name+"is within bounds")	

		
	print 'No. of devices in whitelist are',len(Tag_List)
	
	return Tag_List		


while(1):
	Tag_List = deviceAlerts()
	time.sleep(alertCycleDelay)
