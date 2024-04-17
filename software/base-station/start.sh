#!/bin/bash
echo "Generating Grafana Agent Template"
python3 /app/template.py

echo "Starting Grafana Agent"
# grafana-agent --config.file=/app/grafana-agent.yaml
python3 /app/discovery.py

echo "Starting Alloy"
nohup alloy run /etc/alloy/config.alloy > /app/alloy.log &

while : ; do
  echo "Still alive :) :( :| :D :P ;)"
  python3 /app/discovery.py
  sleep 300
done