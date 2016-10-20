#!/bin/bash

#ps -ef | grep [b]lemaster > /dev/null
COUNT=$(ps -aux | grep -c "python blemaster.py")
echo $COUNT

if [ $COUNT -gt 1 ] 
then

  echo "Process is running."

else

  echo "Process is not running."

  echo "Replace this section with hci down-hci up and blemaster restart process"


  sudo hciconfig hci0 down
  sudo hciconfig hci0 up
  
  sudo /home/pi/ble_launcher.sh &
  
  sleep 25
  
  COUNT=$(ps -aux | grep -c "python blemaster.py")
  echo $COUNT

fi

