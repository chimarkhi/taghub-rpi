import paho.mqtt.client as mqtt
import time as time
from gateway import GatewayParamsStatic


device = GatewayParamsStatic.NAME
azure_username = GatewayParamsStatic.IOTHUB + "/" + GatewayParamsStatic.NAME
azure_password =  GatewayParamsStatic.SAS_KEY
ca_cert_path = "./baltimorebase64.cer"
dev_topic = "devices/"+GatewayParamsStatic.NAME+"/messages/events/"
c2d_topic = "devices/"+GatewayParamsStatic.NAME+"/messages/devicebound/#"

is_conn = 0
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, rc):
    print("Connected with result code "+str(rc))
    is_conn = 1
    client.subscribe(c2d_topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload))

def on_publish(client, userdata, mid):
    print("Sent message")

# The callback for when broker has responded to SUBSCRIBE request.
def on_subscribe(client, userdata, mid, granted_qos):
	print("Subscribed: "+str(mid)+" "+str(granted_qos))

client = mqtt.Client(client_id=device, protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.on_subscribe = on_subscribe
	
client.username_pw_set(username=azure_username,
                       password=azure_password)

client.tls_set("baltimorebase64.cer")
client.connect(GatewayParamsStatic.IOTHUB, port=8883)

#i dont know how to do this in python. wait for mqtt connect to happen before you start publishing
time.sleep(2)

(result,mid)=client.publish(dev_topic,"Test python mqtt client",1)
print result,mid

client.loop_forever()
client.disconnect()
