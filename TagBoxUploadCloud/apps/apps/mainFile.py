#!/usr/bin/python
# settings.py
# Django specific settings
#import os
#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
from django.db import models
from apps.models import *
import threading
import time
import paho.mqtt.client as mqtt
from django.core import serializers

exitFlag = 0
client = mqtt.Client()

class cloudThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        print "Starting " + self.name
        #print_time(self.name, self.counter, 5)
        print "Exiting " + self.name
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect("iot.eclipse.org", 1883, 60)
        client.loop_start()
        operate()

def operate():
    while True:
        # json_data = serializers.serialize('json',localData.objects.all())
        dd = localData.objects.all()
        son_data = serializers.serialize('json',dd)
        time.sleep(2)
        

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("tagboxTopicfromServer")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


# Create new threads
thread1 = cloudThread(1, "Thread-1", 1)

# Start new Threads
thread1.start()

