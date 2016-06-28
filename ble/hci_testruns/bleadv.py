import time
import datetime
import requests
import os


## Superclass containing a tag's info. Can create subclasses later to separate out ble-data 
## and ble-devices lists
 
#class TagInfo:
#	def __init__(self,macid,name,temp,humidity,timestamp,gateway,notified,environment):
#		self.macid='00:00:00:00:00:00'
#		self.name=tagname
#		self.temp=25
#		self.humidity=50
#		self.timestamp=""
#		self.gateway=0
#		self.notified=False
#		self.environment=0


	
## Probable Subclasses not in use currently
##

#class ble_devices(TagInfo):
#	def __init__(self,id,name,notified,environment,gateway):
#		self.notified= False
#		self.environment=0
#
#class ble_data(TagInfo):
#	def __init__(self,temp,humidity,timestamp)
#		self.temp =
#		self.humidity=


## Function to create list of objects containing info of devices 
## linked to this gateway after downloading data from ble-devices list
##

def createDeviceList(device_link):
	
	## Download tags defined in ble_devices and save it in a list of dicts
	r=requests.get(device_link)
	ble_devices=r.json()

	## Create a tuple containing keys of the json data
	data_fields=()
	if ble_devices:
		for key in ble_devices[0]:
			data_fields += (str(key),) 
		
	## Create a list of TagInfo objects filled with data from dled ble_devices list
	
	TagList=[]
	class TagInfo:
		pass
	
	for i in ble_devices:
		tag= TagInfo()
		tag.macid=i['ble_device_id']
		tag.name=i['name']
		tag.notified=i['notified']
		tag.gateway=i['gateway']
		tag.environment=i['environment']
		tag.humidity=0.0
		tag.temp=0.0
		tag.batt=100.0
		tag.timestamp=""
		TagList.append(tag)
	return {'data_fields':data_fields,'TagList':TagList};

def parseAdv(scantime,lib_path,parseOutFile):
	MACID=[]
	Major=[]
	Minor=[]		
	os.system("cd "+lib_path)
	timeout_call = "timeout " + str(scantime) + "s ./ibeacon_scan  -b > scan_out.txt"
	os.system(timeout_call)
	time.sleep(scantime)
	os.system("sort -u scan_out.txt >  ble_data.txt")
	line_num=0
	f_data=open('./ble_data.txt','r')
	f_target=open(parseOutFile,'w')
	for line in f_data:
		data_words=line.split()
		MACID=data_words[0]
		Major=data_words[1]
		Minor=data_words[2]
		temp1 =int(Major[2:4]+Minor[0:2],16)
		humid1=int(Major[0:2]+'00',16)
		batt1=int(Minor[3],16)
		temp=(175.52*temp1/(2**16))-46.85
		humid=(125*temp1/(2**16))-6
		batt=100*16/16
		tstamp=datetime.datetime.now()
		f_target.write(MACID+" "+str(temp)+" "+str(humid)+" "+str(tstamp)+" "+str(batt)+"\n") 
		line_num+=1		

	f_data.close()
	f_target.close()
	return line_num
	
def tagDataUpdate(TagList,advDataFile,gatewayID,passAll):
	updatedTags=[]
	with open(advDataFile,'r') as f_data:
		for line in f_data:
			data_words=line.split()
			for tag in TagList:
				if (tag.macid==data_words[0]) and ((tag.gateway==gatewayID) or passAll):
					tag.temp=data_words[1]
					tag.humidity=data_words[2]
					tag.timestamp=data_words[3]+" "+data_words[4]
					tag.batt=data_words[5]
					updatedTags.append(tag)
	return updatedTags
	


def bleDataUp(data_link,TagList,indexTagsUp,printUpData):
	count=0
	for i in indexTagsUp:
		try:
			r=requests.post(data_link,data={"device":i.macid,"device_datetime":i.timestamp,"humidity":i.humidity,"temperature":i.temp})			
			print i.macid, i.timestamp, i.humidity, i.temp, i.batt
			count+=1
#			if (printUpData==True) and (r.status_code/100==2):
#				print r.status_code, i.macid, i.timestamp, i.humidity, i.temp, i.batt
#				count+=1
#			else:
#				print r.status_code
		except:
			print "Unable to upload/Timeout error"
	return count==len(indexTagsUp)
