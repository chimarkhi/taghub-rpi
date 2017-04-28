#!/bin/bash

ps -ef | grep '[s]udo python mqttClient.py' > /dev/null

if [ $? -eq 0 ]; then
	sudo kill $(ps -ef | grep '[s]udo python mqttClient.py' | awk '{print $2}')
	sudo kill $(ps -ef | grep '[s]udo python blemaster.py' | awk '{print $2}')

	sudo /home/pi/tagbox/startup_config/mqttservice_launcher.sh & > /dev/null
else
	sudo /home/pi/tagbox/startup_config/mqttservice_launcher.sh & > /dev/null
fi
