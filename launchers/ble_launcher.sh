#!/bin/sh

sleep 20
cd /home/pi/tagbox/ble/hci_testruns/
#sudo python blemaster.py | tee /home/pi/log_blemaster.txt
sudo python blemaster.py | tee log_blemaster.txt &
