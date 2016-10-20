#!/bin/sh

sleep 20
cd /home/pi/tagbox/ble/hci_testruns/
sudo python wifidown_alert.py | tee /home/pi/log_wifialert.txt
