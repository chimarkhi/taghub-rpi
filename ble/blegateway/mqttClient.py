#!/usr/bin/python
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
import logging
import ssl
import paho.mqtt.client as mqtt
import requests
import json
import logging.config
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler

from  gateway import GatewayParamsStatic
import gateway
import msgParser
import GatewayParams


broker_type = "azure"
azure_username = GatewayParamsStatic.IOTHUB + "/" + GatewayParamsStatic.NAME
azure_password =  GatewayParamsStatic.SAS_KEY
ca_cert_path = "./baltimorebase64.cer"
dev_topic = "devices/"+GatewayParamsStatic.NAME+"/messages/events/"
c2d_topic = "devices/"+GatewayParamsStatic.NAME+"/messages/devicebound/#"

#sched = BlockingScheduler()
sched = BackgroundScheduler()

# MQTT connection details
if broker_type == "azure" :
	broker = "tbox-dev-hub.azure-devices.net"
	auth = {
	  'username': azure_username,
	  'password' : azure_password
	}
	tls_insecure = False
	mqttPort = 8883
	client_username = GatewayParamsStatic.MQTT_USERNAME
	client_password = GatewayParamsStatic.SAS_KEY
	client_id = GatewayParamsStatic.NAME
	mqttKeepAlive = GatewayParams.MQTT_KEEPALIVE
else :
	broker = "iot.eclipse.org"
	auth = None
	tls_insecure = True
	mqttPort = 1883
	client_username = ""
	client_password = ""
	client_id = GatewayParamsStatic.NAME
	mqttKeepAlive = GatewayParams.MQTT_KEEPALIVE


#D2C acknowledgement post 
def postD2CAck(cmAck):
	payload = { "GwId" : cmAck.GwId,
			"GwTs" : cmAck.GwTs,
			"CmId" : cmAck.CmId,
			"CmResult" : cmAck.CmSt,
			"CmMessage" : cmAck.Message,
			"CmData" : cmAck.CmData
			}
	payload = json.dumps(payload)
	try: 
		r = requests.post(GatewayParamsStatic.D2C_ACK_LINK,data=payload, timeout=GatewayParams.POST_TIMEOUT)	
		if divmod(r.status_code,100)[0] == 2:						
			logger.info('D2C Ack CmId: %s, CmResult: %s successfully sent status: %d', cmAck.CmId, cmAck.CmSt, r.status_code)
			logger.debug("D2C Ack : %s", payload)
		else:
			logger.error("D2C ack post failed, with status : %d", r.status_code)
	except Exception as ex: 
			logger.exception("Exception in D2C ack post %s", ex)		

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	logger.info("Connected with result code "+str(rc))
	client.subscribe(c2d_topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload))
	logger.info("Message recieved from server TOPIC: %s, MSG: %s ", msg.topic, msg.payload)
	try:
		cmAck = msgParser.inMQTTJSON(msg.payload)
		print cmAck.CmId, cmAck.GwTs, cmAck.CmSt
		commandStatus = cmAck.CmSt
		postD2CAck(cmAck)
	except Exception as ex:
		commandStatus = 0
		logger.exception("C2D command flow  failed : %s", ex)
		print("C2D command flow failed : %s", ex)
	finally:
		if commandStatus:
			gateway.appMonitor(hardRestart=True)
			
# The callback for when broker has responded to SUBSCRIBE request.
def on_subscribe(client, userdata, mid, granted_qos):
	print("Subscribed: "+str(mid)+" "+str(granted_qos))
	logger.info("Subscribed: "+str(mid)+" "+str(granted_qos))

# Callback for when client publishes to a topic
def on_publish(mqttc, obj, mid):
	print("mid: "+str(mid))
	logger.info("Published message with mid: "+str(mid))

class MQTTClient():
	def __init__(self,broker_type):
		self.c = mqtt.Client(client_id=client_id, clean_session = False,protocol = mqtt.MQTTv311)
		self.c.username_pw_set(username = client_username, password=client_password)
		if broker_type == "azure":
			self.c.tls_set(ca_cert_path)
		self.c.tls_insecure_set(tls_insecure)
		self.c.on_connect = on_connect
		self.c.on_message = on_message
		self.c.on_subscribe = on_subscribe
		self.c.on_publish = on_publish
	def subscribe(self):
		self.c.connect(broker,mqttPort,mqttKeepAlive)
		self.c.loop_forever()
	def disconnect(self):
		self.c.loop_stop()
		self.c.disconnect()
	def pubSingle(self,payloadPacket):
		self.c.connect(broker,mqttPort,mqttKeepAlive)
		(r,mid) = self.c.publish(dev_topic,payload = payloadPacket, qos =1)
		self.c.disconnect()
		return (r,mid)

def mqttPublish(payloadPacket):
	r = publish.single(dev_topic,
	payload = payloadPacket,
	hostname = broker,
	client_id = client_id,
	auth=auth,
	tls=tls,
	port=mqttPort,
	qos = 1)	
	return r

@sched.scheduled_job('interval',minutes = GatewayParams.BLEMONITOR_INTERVAL)
def bleMonitor():
	gateway.appMonitor(hardRestart=False)


if __name__ == "__main__" :
	logging.config.fileConfig('./logging.conf',
				disable_existing_loggers = False,
				defaults={'logFileName'	:GatewayParamsStatic.LOGFILE_MQTT,
					  'logLevel'	:GatewayParams.LOGLEVEL,
					  'logFileSize' :GatewayParams.LOGFILE_SIZE,
					  'logBackupCount':GatewayParams.LOG_BACKUPS })
					  
	logger = logging.getLogger('__main__')	
	
	gateway.appMonitor(hardRestart=False)
	logger.info("blemaster process started")
	
	logger.info("Starting scheduler")	
	sched.start()

	mqtter = MQTTClient(broker_type)
	(r,mid) = mqtter.pubSingle("testup through method")
	print "through method", r,mid	
	mqtter.subscribe()

