import time
import datetime
import requests
import os
import bleadv

## Variables
scan_iterations=10 # unused
i=0		
lib_path="/home/pi/tagbox/ble/hci_testruns/" # dir path
scantime=10 #scan duration in secs
sleeptime=120 # sleep duration in secs
gatewayID=4  # gateway/room ID as specified in server data lists	
passAll=True # Set true to ignore gatewayID and update/upload all scanned tags
printUpData=True # Set true for displaying the uploaded data

## temp file names
advDataFile='./ble_data_parsed.txt'

## Link to lists in cloud
data_link='https://bliss-rdt.herokuapp.com/api/ble-data/'
device_link='https://bliss-rdt.herokuapp.com/api/ble-device/'

while (1):
	## calling createDeviceList function to get ble_device list data
	Tag_List=bleadv.createDeviceList(device_link)
	print('No. of devices in whitelist are: %d' %len(Tag_List))


	## calling parseAdv to scan for ble devices, parse their adv packets and print out adv data
	## in ble_data_parsed.txt
	numTagsFound=bleadv.parseAdv(scantime,lib_path,advDataFile)
	print('No. of advertisers scanned are: %d' %numTagsFound)

	## update temp, humidity and timestamp in Tag_List based on the adv data
	indexTagsUp=bleadv.tagDataUpdate(Tag_List,advDataFile,gatewayID,passAll)
	print('No. of tags updated are: %d' %len(indexTagsUp))
	#print 'Index of updated tags: ', indexTagsup[:]
 
	## upload data (this needs to be optimized to upload only newly updated items)
	upload_status=bleadv.bleDataUp(data_link,Tag_List,indexTagsUp,printUpData)
	print 'All identified tags updated :', upload_status
	
	time.sleep(sleeptime)
