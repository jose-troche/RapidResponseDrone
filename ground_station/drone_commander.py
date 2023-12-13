import socket
from database import SHUTDOWN, DRONE_TELEMETRY
from multiprocessing.managers import DictProxy

TELLO_IP = '192.168.10.1'
TELLO_TELEMETRY_PORT = 8890
TELLO_COMMAND_PORT = 8889
TELLO_COMMAND_ADDRESS = (TELLO_IP, TELLO_COMMAND_PORT)

UDP_SOCKET = socket.socket(socket.AF_INET,    # Internet
                           socket.SOCK_DGRAM) # UDP


# Send a command to the drone via the UDP socket
def send_command_to_drone(command: str):
    if command in set(['takeoff', 'streamon']):
        send_command_to_drone('command')

    UDP_SOCKET.sendto(command.encode(), TELLO_COMMAND_ADDRESS)

def drone_telemetry_listener(db: DictProxy):
    telemetry_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    telemetry_socket.bind(('', TELLO_TELEMETRY_PORT))

    while not db.get(SHUTDOWN, False):
        data, _ = telemetry_socket.recvfrom(1024)
        data_dict = {}
        for item in data.decode().split(';'):
            if ':' in item:
                k, v = item.split(':')
                data_dict[k] = v

        db[DRONE_TELEMETRY] = data_dict

    print('Shutting down the Drone Telemetry Listener')

    telemetry_socket.close()
