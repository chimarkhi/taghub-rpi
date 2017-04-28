#!/bin/sh

sleep 10
#cd /home/pi/tagbox/ble/hci_testruns/
cd /home/pi/tagbox/ble/blegateway/

sleep 5

#sudo python blemaster_test.py > /home/pi/log_blemaster_test.txt
#sudo python blemaster_azure.py > /home/pi/tagbox/ble/hci_testruns/log_blemaster.txt
sudo python mqttClient.py 
