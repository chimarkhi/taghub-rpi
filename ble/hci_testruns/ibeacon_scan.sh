#!/bin/bash

if [[ $1 == "parse" ]]; then
  packet=""
  capturing=""
  count=0
  while read line
  do
    count=$[count + 1]
    if [ "$capturing" ]; then
      if [[ $line =~ ^[0-9a-fA-F]{2}\ [0-9a-fA-F] ]]; then
        packet="$packet $line"
      else
        if [[ $packet =~ ^04\ 3E\ 2B\ 02\ 01\ .{26}\ 02\ 01\ .{14}\ 02\ 15 ]]; then
#          UUID=`echo $packet | sed 's/^.\{69\}\(.\{47\}\).*$/\1/'`
          MACID=`echo $packet | sed 's/^.\{21\}\(.\{17\}\).*$/\1/'`
          MAJOR=`echo $packet | sed 's/^.\{117\}\(.\{5\}\).*$/\1/'`
          MINOR=`echo $packet | sed 's/^.\{123\}\(.\{5\}\).*$/\1/'`
#          POWER=`echo $packet | sed 's/^.\{129\}\(.\{2\}\).*$/\1/'`

          MACID=`echo $MACID | sed 's/\ //g'`
	  MAJOR=`echo $MAJOR | sed 's/\ //g'`
          MINOR=`echo $MINOR | sed 's/\ //g'`

          if [[ $2 == "-b" ]]; then
	    echo "$MACID $MAJOR $MINOR" | uniq
          else
    	    echo "MACID: $MACID MAJOR: $MAJOR MINOR: $MINOR"
          fi
        fi
        capturing=""
        packet=""
      fi
    fi

    if [ ! "$capturing" ]; then
      if [[ $line =~ ^\> ]]; then
        packet=`echo $line | sed 's/^>.\(.*$\)/\1/'`
        capturing=1
      fi
    fi
  done
else
  sudo hciconfig hci0 down
  sudo hciconfig hci0 up	
  sudo hcitool lescan --duplicates 1>/dev/null &
  if [ "$(pidof hcitool)" ]; then
    sudo hcidump --raw | ./$0 parse $1
  fi
fi
