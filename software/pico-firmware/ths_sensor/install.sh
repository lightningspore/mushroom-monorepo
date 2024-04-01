#!/bin/bash

INSTALL_VOLUME=/Volumes/CIRCUITPY

circup install -r requirements-circuitpython.txt

echo "listing install volume"
ls $INSTALL_VOLUME
cp -r lib/* $INSTALL_VOLUME/lib


read -p "Do you want to copy the settings.toml file? (y/n) " answer
if [[ $answer = y* ]]; then
    cp settings.toml $INSTALL_VOLUME
    echo "settings.toml copied successfully."
else
    echo "Skipping settings.toml copy."
fi

cp code.py $INSTALL_VOLUME
