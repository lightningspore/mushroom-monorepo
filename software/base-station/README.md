# base-station
The base station is a central application which is running Grafana Alloy, which discovers sensor modules running on the network, and polls them at a specified interval. It then sends that data back to Grafana Cloud so it can be graphed and analyzed.

The benefit of a central base station to handle this job, is that the code running on the sensor modules themselves can be extremely simple. Sensor modules do not need to know anything about MQTT, or any other specialized communication protocol, all it is required to do is read sensor data, and expose that sensor data in prometheus format using a web server.

## Build/Deploy Image to Balena
```bash
./build.sh
```