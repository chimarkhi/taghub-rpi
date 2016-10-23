import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import time

mqttc=mqtt.Client()
mqttc.connect("m2m.eclipse.org",1883, 60)

mqttc.loop_start()
while True:
	mqttc.publish("tagbox/tag001/major", "2");
	mqttc.publish("tagbox/tag001/minor", "3");
	time.sleep(3)
