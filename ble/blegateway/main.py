import os
from bluepy.btle import Scanner

from scan import DeviceForwardingDelegate
#from persistence import DataPersistence
#from igrill import IGrillHandler
#from tokencube import TokenCubeHandler

device_settings = {
    "d4:81:ca:21:86:db": {
        "device": "iGrill Mini",
        "addr": "d4:81:ca:21:86:db",
        "type": "kitchen"
    },
}


if __name__ == "__main__":
    print "Creating Scanner"
    delegate = DeviceForwardingDelegate()
    delegate.handlers.append(IGrillHandler(device_settings))

    scanner = Scanner(0)
    scanner.withDelegate(delegate)

    print "Connecting to InfluxDB server"
    persistence = DataPersistence(INFLUX_SERVER, INFLUX_DATABASE, INFLUX_USER, INFLUX_PASSWORD)

    while True:
        print "Scanning..."
	scanner.scan(10.0)
	print "Persisting..."
	for handler in delegate.handlers:
		print("inside for")
		handler.persist_stats()
	
