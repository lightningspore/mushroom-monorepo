# Camera Server
This project will start a web server on a device and return images taken from a webcam from that device.

Features:
- UVC control of webcam


## Special Instructions for Raspberry Pi
Install
```bash
sudo apt-get install build-essential cmake unzip pkg-config
sudo apt-get install libusb-1.0-0-dev
sudo apt-get install libjpeg-dev
sudo apt-get install libturbojpeg0-dev
pip install -vvv pupil-labs-uvc --timeout=60 --retries=10
```

Run it
```bash
sudo su
. /home/skorn/.cache/pypoetry/virtualenvs/camera-server-5qWbIdxS-py3.9/bin/activate
python3 server.py
```