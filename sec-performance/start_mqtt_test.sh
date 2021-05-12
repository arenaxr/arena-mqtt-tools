#!/bin/bash

SEED=$(date +%s) # same seed for all started in the loop
for i in {0..5}
do
  make mqtt-auth-tester.py ARGS="-s $SEED" > log.txt &
done

echo "Waiting..."
wait < <(jobs -p)

SEED=$(date +%s) # same seed for all started in the loop
for i in {0..5}
do
  make mqtt-auth-tester.py ARGS="-s $SEED" > log.txt &
done

echo "Waiting..."
wait < <(jobs -p)

SEED=$(date +%s) # same seed for all started in the loop
for i in {0..5}
do
  make mqtt-auth-tester.py ARGS="-s $SEED --nosec" > log_nosec.txt &
done

echo "Waiting..."
wait < <(jobs -p)

SEED=$(date +%s) # same seed for all started in the loop
for i in {0..5}
do
  make mqtt-auth-tester.py ARGS="-s $SEED --nosec" > log_nosec.txt&
done

echo "Waiting..."
wait < <(jobs -p)
echo "Done!"
