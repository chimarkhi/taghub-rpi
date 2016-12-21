from bluepy.btle import Scanner, DefaultDelegate, Peripheral, ADDR_TYPE_RANDOM, AssignedNumbers
import time
import datetime

class ScanDelegate(DefaultDelegate):
	def __init__(self):
		DefaultDelegate.__init__(self)

	def handleDiscovery(self, dev, isNewDev, isNewData):
		if isNewDev:
			pass
#			print "Discovered device", dev.addr
		elif isNewData:
			pass
#			print "Received new data from", dev.addr

class TempProbe(Peripheral):
	def __init__(self,addr):
		Peripheral.__init__(self,addr,addrType=ADDR_TYPE_RANDOM)
	
	

tempserviceUUID = "fe551580-4180-8a02-ef2c-1b42a0ac3f83"
tempcharUUID = "fe551582-4180-8a02-ef2c-1b42a0ac3f83"
manufacturerCappec = "59002d01589086ea01"
typeCompanyName = 255
probe = None

scanWindow = 10

cappecID1 = "ea:86:90:58:01:2d" 
cappecID2 = "e6:c4:08:69:bd:66" 

tempOutFile = "cappec_data_out.txt" 


while (1):
	try:
		scanner = Scanner().withDelegate(ScanDelegate())
		devices = scanner.scan(scanWindow)

	
		for dev in devices:
#			print "Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi)
			for (adtype, desc, value) in dev.getScanData():
#				print "  %s: %s = %s" % (adtype, desc, value)
				if (adtype == typeCompanyName) and (value == manufacturerCappec) \
						and ((dev.addr == cappecID1) or (dev.addr == cappecID2)):
					try:
						probe = TempProbe(dev.addr)
#						print("connected")
#						service, = [s for s in probe.getServices() if s.uuid==tempserviceUUID]
#        					print service.uuid
						ccc, = probe.getCharacteristics(uuid=tempcharUUID)
						temp_data=ccc.read()
#						print temp_data.encode('hex')
						tempProbeOne = round(((ord(temp_data[0])-32)*5.0/9),2)  
						tempProbeTwo = round(((ord(temp_data[2])-32)*5.0/9),2)  
						print datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"Temp:", tempProbeOne, tempProbeTwo 
						f_target=open(tempOutFile,'a+')
						f_target.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+",Temp,"+ str(tempProbeOne)+ "," +str(tempProbeTwo)+"\n") 
						f_target.close()
					except Exception, error:
						print("The error is:",str(error))
					finally:
						if probe:
							probe.disconnect()
	except Exception, error:
		print("The error is:",str(error))

	time.sleep(20)
