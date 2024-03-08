import serial
from time import sleep
from datetime import datetime

# Replace '/dev/tty.board_name' with the appropriate serial port name
# serial_port = '/dev/tty.usbmodem1101'
serial_port = '/dev/ttyACM0'

baud_rate = 115200  # Adjust as needed

def read_line_from_serial():
    # Read a line from the serial port
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        data = ser.readline().decode('utf-8').rstrip()
        # print(data)
        return data

# Read a line f
while True:
    # print("reading line: ")
    data = read_line_from_serial()
    if "Auto-reload is on." in data:
        pass
    else:
        print(data)
    # print(f"{ datetime.now().isoformat()} --- {temp_data:.3f} degF")
    # sleep(1)