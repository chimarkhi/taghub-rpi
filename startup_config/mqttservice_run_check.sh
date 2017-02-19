#!/bin/bash

ps -ef | grep [m]qttClient.py > /dev/null

if [ $? -eq 0 ]; then
  echo "Process is running."
else
  echo "Process is not running."
  echo "hci down-hci up and mqttClient restart process"
  sudo hciconfig hci0 down
  sudo /home/pi/tagbox/startup_config/mqttservice_launcher.sh &
fi

