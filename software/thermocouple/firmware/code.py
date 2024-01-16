import time
import board
import busio
from adafruit_mcp9600 import adafruit_mcp9600

i2c = busio.I2C(board.GP5, board.GP4, frequency=100000)
mcp = adafruit_mcp9600.MCP9600(i2c, address=96)

while True:
    print(mcp.temperature*(9/5) + 32)
    time.sleep(1)