SCAN_WINDOW = 15 ## seconds the scan window is open for 
SCAN_INTERVAL = 150 ##seconds scan interval 
UPLOAD_INTERVAL = 150 ## interval (seconds) at which payload is created and posted 
PACKET_SIZE = 3500 ## bytes, max payload size 
MAX_PACKET_UNITS = 20 ## max data points in one payload 
DBFLUSH_INTERVAL = 6 ## hours, interval at which db is flushed of data older than KEEPDATA_DAYS 
KEEPDATA_DAYS = 4 ## days till which data is archived 
MAX_PROBECON_ATTEMPTS = 5 ## max connect attempts to a peripheral 
POST_TIMEOUT = 120 ## seconds, post request timeout 
MQTT_KEEPALIVE = 60 					## seconds for which the connection is kept alive 	
LOGLEVEL = "DEBUG" ## logging level 
LOGFILE_SIZE = 1000000		## size of logfile
LOG_BACKUPS = 2			## number of backup files
READNRG = 0			## read modbus for energy data
WHITELIST_ENABLE = 0 ## 0,1,2,3 enable whitelisting levels 
COMMTYPE = "HTTPS" ## HTTPS, MQTT 
WHITELISTREAD_INTERVAL =6 	## REMOVE FROM blemaster.py
BLE_ENABLE = 1			## Enable ble radio
LOG_UPLOAD_INTERVAL = 1		## Log file upload interval in hours


