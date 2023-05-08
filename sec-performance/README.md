# Broker security performance tests

Runs connnect, subscribe, publish tests against brokers configured with and without security.

Setup assumes brokers are run in one node and clients (test python scripts) on another. The brokers run a [modified mosquitto broker](https://github.com/SilverLineFramework/mosquitto-broker/tree/timing_log) that logs connect, publish and subscribe handler time.

## Broker config

On the host running the brokers, clone this repo and copy the `sec-performance/server-config` folder (see note below). Start the two brokers using the compose file:
```
docker-compose up
```

**Note:**: the config uses the certificate files from an arena deployment and assumes that `../arena-services-docker` exists, so you need to copy the `server-config` folder to a folder with the same parent as `arena-services-docker`. A test deployment is at **arena0**, folder `~/mosquitto-broker-test`.

The compose file starts two brokers. One configured with security and another with no security. The broker is a modified mosquitto (`conixcenter/arena-broker-test`) that ouputs log messages of `handle_connection`, `handle_subscription`, and `handle_publish` timming.

The configuration of the brokers are in the `mosquitto-sec.conf` and `mosquitto-nosec.conf` files. The brokers are configured to send log messages (`log_type notice` and above) to a topic (config option `log_dest topic` sends log messages to `$SYS/broker/log/N`).


## Client tests

On the host running the tests, we need to start logging (this can be on a third node) and then start the tests.

### Start logging

We save the messages sent to `$SYS/broker/log/N` for later processing with an helper bash script:
```
start_log_server_time.sh
```
This script starts a `mosquitto_sub` client using the config (mqtt user, password, host, port) in **secrets.env**.
**Note**: create `secrets.env` from the example before starting logging. The logs are saved to a folder **logs**.

### Start tests

Test are executed by `mqtt-tester.py` to start several instances of it, we use an helper script too:
```
start_mqtt_test.sh
```

## Parsing the logs

The logs are parsed using the jupyter notebook in `analize-logs.ipynb`. Update the notebook to use the latest log files.


