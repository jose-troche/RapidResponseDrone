#!/usr/bin/env python3

import threading
import time
import asyncio
from queue import Queue
from bleak import BleakClient, BleakScanner


UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

def handle_disconnect(client: BleakClient):
    print("Device was disconnected")


def laser_commander(queue: Queue):
    device = None
    loop = asyncio.new_event_loop()

    try:
        while True:

            print("Scanning to find a LASER device ...")
            
            device = loop.run_until_complete(BleakScanner.find_device_by_name('LASER', timeout=4.0))

            if device is None:
                print("No LASER device found. Will try again later")    
            else:
                client = BleakClient(device, disconnected_callback=handle_disconnect)
                loop.run_until_complete(client.connect())
                print("Connected to LASER device")

                uart = client.services.get_service(UART_SERVICE_UUID)
                tx_characteristic = uart.get_characteristic(UART_TX_CHAR_UUID)

                while client:
                    # Wait for an item in the queue
                    queue.get() 

                    # Send a fire command to the laser: 'on' followed by the number of on/off cycles
                    print("Firing LASER")
                    loop.run_until_complete(client.write_gatt_char(tx_characteristic, b'on 6', response=False))

                    queue.task_done()

            time.sleep(1)
    finally:
        print("Closing asyncio loop")
        loop.close()

if __name__ == "__main__":
    queue = Queue()

    threading.Thread(target=laser_commander, args=(queue,)).start()

    while True:
        queue.put_nowait(1)
        time.sleep(4)
