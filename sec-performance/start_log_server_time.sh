#!/bin/bash

source secrets.env

LOG_FILE_DATE=$(date +%F_%H-%M-%S.%3N)

mkdir -p logs

LOG_FILE_SEC="logs/server_time_sec_${LOG_FILE_DATE}.log"
LOG_FILE_NOSEC="logs/server_time_nosec${LOG_FILE_DATE}.log"

echo "Starting logging to $LOG_FILE_SEC $LOG_FILE_NOSEC"
pids=()
mosquitto_sub --capath /etc/ssl/certs/ -h $MQTT_HOST -p $MQTT_PORT_SEC -u $MQTT_USER -P $MQTT_PASS -t '$SYS/broker/log/N' > $LOG_FILE_SEC &
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
