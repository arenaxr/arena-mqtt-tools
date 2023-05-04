#!/bin/bash

for i in {0..500}
do
  make mqtt-tester.py ARGS="--exit_on_conn" &
done

for i in {0..500}
do
  make mqtt-tester.py ARGS="--nosec --exit_on_conn" &
done

echo "Waiting..."
wait < <(jobs -p)
echo "Done!"
