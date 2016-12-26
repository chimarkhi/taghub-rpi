from bluepy.btle import Scanner, DefaultDelegate, Peripheral, ADDR_TYPE_RANDOM, AssignedNumbers
import time
import struct


class ScanDelegate(DefaultDelegate):
	def __init__(self):
		DefaultDelegate.__init__(self)

	def handleDiscovery(self, dev, isNewDev, isNewData):
		if isNewDev:
			pass
			print "Discovered device", dev.addr
		elif isNewData:
			pass
			print "Received new data from", dev.addr

class TempProbe(Peripheral):
	def __init__(self,addr):
		Peripheral.__init__(self,addr,addrType=ADDR_TYPE_RANDOM)
	
	

tempserviceUUID = "fe551580-4180-8a02-ef2c-1b42a0ac3f83"
tempcharUUID = "fe551582-4180-8a02-ef2c-1b42a0ac3f83"
manufacturerCappec = "59002d01589086ea01"
typeCompanyName = 255
probe = None

scanWindow = 10


try:
	scanner = Scanner().withDelegate(ScanDelegate())
	devices = scanner.scan(scanWindow)
except Exception, error:
	print("The error is:",str(error))
	
for dev in devices:
	print "Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi)
	print dev.serviceData
	if 'ffe1' in dev.serviceData.keys():
		print 'ITS HERE'
	for (adtype, desc, value) in dev.getScanData():
		print "  %s: %s = %s" % (adtype, desc, value)
		if (adtype == typeCompanyName) and (value == manufacturerCappec):
			try:
				probe = TempProbe(dev.addr)
				print("connected")
#				service, = [s for s in probe.getServices() if s.uuid==tempserviceUUID]
#        			print service.uuid
				ccc, = probe.getCharacteristics(uuid=tempcharUUID)
				temp_data=ccc.read()
				print temp_data.encode('hex')
				tempProbeOne = (ord(temp_data[0])-32)*5/9  
				tempProbeTwo = (ord(temp_data[2])-32)*5/9  
				print("Temp:",tempProbeOne, tempProbeTwo)
			except Exception, error:
				print("The error is:",str(error))
			finally:
				if probe:
					probe.disconnect()

