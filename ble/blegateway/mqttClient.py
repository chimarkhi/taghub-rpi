import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import time
import logging
import ssl

from  gateway import GatewayParamsStatic
import gateway
import msgParser
import GatewayParams

broker_type = "notazure"
azure_username = GatewayParamsStatic.IOTHUB + "/" + GatewayParamsStatic.NAME
azure_password =  GatewayParamsStatic.SAS_KEY
ca_cert_path = "/etc/ssl/certs/ca-certificates.crt"
dev_topic = "devices/"+GatewayParamsStatic.NAME+"/messages/events/"
c2d_topic = "devices/"+GatewayParamsStatic.NAME+"/messages/devicebound/"


# MQTT connection details
if broker_type == "azure" :
	broker = "tbox-dev-hub.azure-devices.net"
	auth = {
	  'username': azure_username,
	  'password' : azure_password
	}
	tls = {
	  'ca_certs' : ca_cert_path,
	  'tls_version' : ssl.PROTOCOL_TLSv1
	}
	mqttPort = 8883
	client_username = GatewayParamsStatic.MQTT_USERNAME
	client_password = GatewayParamsStatic.SAS_KEY
	client_id = GatewayParamsStatic.NAME
	mqttKeepAlive = GatewayParams.MQTT_KEEPALIVE
else :
	broker = "iot.eclipse.org"
	auth = None
	tls = None
	mqttPort = 1883
	client_username = ""
	client_password = ""
	client_id = GatewayParamsStatic.NAME
	mqttKeepAlive = GatewayParams.MQTT_KEEPALIVE


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	logging.info("Connected with result code "+str(rc))
	client.subscribe(c2d_topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload))
	logging.info("Message recieved from server TOPIC: %s, MSG: %s ", msg.topic, msg.payload)
	try:
		cmAck = msgParser.inMQTTJSON(msg.payload)
		print cmAck.CmId, cmAck.GwTs, cmAck.CmSt
		gateway.appRestart()
	except Exception as ex:
		logging.exception("C2D message parsing failed : %s", ex)
		print("C2D message parsing failed : %s", ex)

# The callback for when broker has responded to SUBSCRIBE request.
def on_subscribe(client, userdata, mid, granted_qos):
	print("Subscribed: "+str(mid)+" "+str(granted_qos))
	logging.info("Subscribed: "+str(mid)+" "+str(granted_qos))

# Callback for when client publishes to a topic
def on_publish(mqttc, obj, mid):
	print("mid: "+str(mid))
	logging.info("Published message with mid: "+str(mid))

class MQTTClient():
	def __init__(self):
		self.c = mqtt.Client(client_id=client_id, clean_session = False)
		self.c.username_pw_set(username = client_username, password=client_password)
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

def main() :
	logging.basicConfig(filename=GatewayParamsStatic.LOGFILE_MQTT, filemode = 'w', 
						format='[%(asctime)s] %(levelname)s %(message)s', 
						datefmt='%Y-%m-%d %H:%M:%S',  
						level = GatewayParams.LOGLEVEL)
	logging.info('Logging started')	
	

if __name__ == "__main__":
	main()
	mqtter = MQTTClient()
	(r,mid) = mqtter.pubSingle("testup through method")
	print "through method", r,mid	
	mqtter.subscribe()
	


