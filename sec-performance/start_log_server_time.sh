#!/bin/bash

source secrets.env
LOG_FILE_SEC=server_time_sec.log
LOG_FILE_NOSEC=server_time_nosec.log

LOG_FILE_DATE=$(date +%F_%T| tr ':' '_')
[ -f server_time_sec.log ] && mv server_time_sec.log logs/server_time_${LOG_FILE_DATE}_sec.log
[ -f server_time_nosec.log ] && mv server_time_nosec.log logs/server_time_${LOG_FILE_DATE}_nosec.log

echo "Starting logging to $LOG_FILE_SEC $LOG_FILE_NOSEC"
pids=()
mosquitto_sub -h $MQTT_HOST -p $MQTT_PORT_SEC -u $MQTT_USER -P $MQTT_PASS -t '$SYS/broker/log/N' > $LOG_FILE_SEC &
pids+=( $! )
mosquitto_sub -h $MQTT_HOST -p $MQTT_PORT_NOSEC -t '$SYS/broker/log/N' > $LOG_FILE_NOSEC &
pids+=( $! )

while true; do
    echo "Press Q to finish logging!"
    read -n1 -s input
    if [[ $input = "q" ]] || [[ $input = "Q" ]]
        then break
    fi
done

for pid in ${!pids[@]};
do
  kill $pid
done
