#!/usr/bin/env python3

import threading
import time
import asyncio
import sigint_handler
from bleak import BleakClient, BleakScanner


def laser_commander(fire_event: threading.Event):
    UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
    UART_TX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

    loop = asyncio.new_event_loop()

    def handle_disconnect(_: BleakClient):
        print("LASER device was disconnected. Cancelling all tasks in the asyncio loop")
        for task in asyncio.all_tasks(loop):
            task.cancel()

    try:
        device = None
        while device is None:
            print("Scanning to find a LASER device ...")
            device = loop.run_until_complete(BleakScanner.find_device_by_name('LASER'))

        client = BleakClient(device, disconnected_callback=handle_disconnect)
        loop.run_until_complete(client.connect())
        print("Connected to LASER device")

        uart = client.services.get_service(UART_SERVICE_UUID)
        tx_characteristic = uart.get_characteristic(UART_TX_CHAR_UUID)

        while client:
            # Wait for a fire event
            fire_event.wait()

            # Send a fire command to the laser: 'on' followed by the number of on/off cycles
            print("LASER ON")
            loop.run_until_complete(client.write_gatt_char(tx_characteristic, b'on 4', response=False))

            fire_event.clear()

        print('Shutting down the Laser Commander')

    except asyncio.CancelledError:
        print("LASER: all tasks in asyncio loop have been cancelled")
    finally:
        print("LASER: closing asyncio loop")
        loop.close()


def start_laser_commander(fire_event: threading.Event):
    laser_commander_thread = threading.Thread(target=laser_commander, args=(fire_event,), daemon=True)
    laser_commander_thread.start()
    return laser_commander_thread


if __name__ == "__main__":
    fire_event = threading.Event()

    while not sigint_handler.shutdown_signal:
        print("Starting LASER commander thread")
        laser_commander_thread = start_laser_commander(fire_event)

        while laser_commander_thread.is_alive() and not sigint_handler.shutdown_signal:
            print("Time", int(time.monotonic()))
            fire_event.set()
            time.sleep(5)

    print('Main process shutting down')
