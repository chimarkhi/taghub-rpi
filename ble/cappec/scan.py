from bluepy.btle import Scanner, DefaultDelegate, Peripheral, ADDR_TYPE_RANDOM, AssignedNumbers

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
def FindPeripheral():
    service = btle.Scanner()
    while True:
        scanresults = service.scan(2)
        for scanresult in scanresults:
            name = scanresult.getValueText(8)
            print "Found ", scanresult.addr, name

            if name == "iGrill_mini":
                return IGrillMiniPeripheral(scanresult.addr)
