#!/bin/bash

ps -ef | grep [b]lemaster.py > /dev/null

if [ $? -eq 0 ]; then
  echo "Process is running."
else
  echo "Process is not running."
  echo "Replace this section with hci down-hci up and blemaster restart process"
  sudo hciconfig hci0 down
  sudo /home/pi/tagbox/startup_config/ble_launcher.sh &
fi

