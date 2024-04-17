#!/bin/bash
echo "Discovering sensors on the network..."
python3 /app/discovery.py

echo "Starting Alloy"
nohup alloy run /etc/alloy/config.alloy \
  --server.http.listen-addr=0.0.0.0:12345 \
  > /app/alloy.log &

while : ; do
  echo "Still alive :) :( :| :D :P ;)"
  python3 /app/discovery.py
  sleep 300
done