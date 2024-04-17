#!/bin/bash

while : ; do
  echo "Still alive :) :( :| :D :P ;)"
  echo "Discovering sensors on the network..."
  python3 /app/discovery.py
  sleep 300
done