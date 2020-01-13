#!/bin/bash

PRIMARY='eDP1'
MONITOR=$(xrandr | grep -v disconnected | grep connected | grep -v $PRIMARY | cut -d' ' -f1)
MIRROR=0

while [[ $# -gt 0 ]];
do
   echo $1
   case $1 in
    	-m|--mirror)
    	MIRROR=1
    	shift # past argument
	shift
    	;;
   esac
done

if [ -z "$MONITOR" ]; then
	echo "turning off monitors"
	CONNECTED_MONITORS=$(xrandr --listactivemonitors | grep -v $PRIMARY | grep -v Monitors | rev | cut -d' ' -f1 | rev)
	for m in $CONNECTED_MONITORS; do
		xrandr --output $m --off
	done
else
	echo "configuring $MONITOR"
	if [ $MIRROR -eq 1 ]; then
		xrandr --output $MONITOR --auto --same-as $PRIMARY
	else
		xrandr --output $MONITOR --auto --above $PRIMARY
		i3-msg workspace 10, move workspace to output $MONITOR
		for i in $(seq 1 9); do 
			i3-msg workspace $i, move workspace to $PRIMARY; 
		done
		i3-msg workspace 10
	fi
fi
