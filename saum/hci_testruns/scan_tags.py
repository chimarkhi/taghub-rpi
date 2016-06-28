import time
import datetime
import requests
import os

i=0
TIMEOUT_lescan = "20s"
while (i<10):
	MACID_all=[]
	Major_all=[]
	Minor_all=[]
	MACID=[]
	Major=[]
	Minor=[]	
	os.system("cd /home/pi/tagbox/ble/hci_testruns/ ")
	os.system("timeout 15s ./ibeacon_scan  -b > scan_out.txt")
	time.sleep(15)
	os.system("sort -u scan_out.txt >  ble_data.txt")
	
	j=0
	f_data=open('./ble_data.txt','r')
	for line in f_data:
		data_words=line.split()
		MACID_all.append(data_words[0]);
		Major_all.append(data_words[1]);
		Minor_all.append(data_words[2]);
		MACID=data_words[0]
		Major=data_words[1]
		Minor=data_words[2]
		temp1 =int(Major[2:4]+Minor[0:2],16)
		humid1=int(Major[0:2]+'00',16)
		temp=(175.52*temp1/(2**16))-46.85
		humid=(125*temp1/(2**16))-6
		j=j+1
		tstamp=datetime.datetime.now()
		print(MACID_all)
		print(MACID,temp,humid)
	        r=requests.post('https://bliss-rdt.herokuapp.com/api/ble-data/',data={"timestamp":tstamp,"temperature":temp,"humidity":humid,"device":"1"})
	f_data.close()
	
	time.sleep(10)
	i=i+1
	



