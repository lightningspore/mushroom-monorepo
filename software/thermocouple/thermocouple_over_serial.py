import serial
from time import sleep
from datetime import datetime

# Replace '/dev/tty.board_name' with the appropriate serial port name
serial_port = '/dev/tty.usbmodem11101'
baud_rate = 115200  # Adjust as needed

def read_line_from_serial(ser):
    # Read a line from the serial port
    data = ser.readline().decode('utf-8').rstrip()
    # print(data)
    result = float(data)
    return result

try:
    with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
        temp_data = read_line_from_serial(ser)
except serial.SerialException as e:
    print(f"Error: {e}")


while True:
    try:
        with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
            temp_data = read_line_from_serial(ser)
    except serial.SerialException as e:
        print(f"Error: {e}")

    print(f"{ datetime.now().isoformat()} --- {temp_data:.3f} degF")
    sleep(1)