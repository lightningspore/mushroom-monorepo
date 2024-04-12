#!/bin/bash
echo "Generating Grafana Agent Template"
python3 /app/template.py

echo "Starting Grafana Agent"
grafana-agent --config.file=/app/grafana-agent.yaml

while : ; do
  echo "Still alive :) :( :| :D :P ;)"
  sleep 15
done