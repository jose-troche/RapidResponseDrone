# Listen on BlueTooth and turn on laser if 'on' is received
import time
import board
from digitalio import DigitalInOut, Direction

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

led = DigitalInOut(board.D0)
led.direction = Direction.OUTPUT
led.value = False

LASER_ON = "on"

def laser_on():
    sleep_secs = 0.2
    led.value = True
    time.sleep(sleep_secs)
    led.value = False
    time.sleep(sleep_secs)

def send(msg):
    uart.write(str(msg).encode("utf-8"))

while True:
    ble.start_advertising(advertisement)
    print("Waiting to connect ...")
    while not ble.connected:
        pass
    print("Connected")
    while ble.connected:
        data = uart.readline().decode().strip()
        if data:
            arr = data.split()
            if arr[0] == LASER_ON:
                try:
                    n = int(arr[1])
                except:
                    n = 7
                send(f"LASER {n} times")
                for i in range(n):
                    laser_on()
            else:
                send(f"Received: {data}")
