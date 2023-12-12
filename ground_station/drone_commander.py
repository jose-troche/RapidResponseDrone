import socket
import time

TELLO_IP = '192.168.10.1'
TELLO_COMMAND_PORT = 8889
TELLO_COMMAND_ADDRESS = (TELLO_IP, TELLO_COMMAND_PORT)

UDP_SOCKET = socket.socket(socket.AF_INET,    # Internet
                           socket.SOCK_DGRAM) # UDP


# Send a command to the drone via the UDP socket
def send_command_to_drone(command: str):
    if command in set(['takeoff', 'streamon']):
        send_command_to_drone('command')

    UDP_SOCKET.sendto(command.encode(), TELLO_COMMAND_ADDRESS)

# Start this on a thread
# Note: in experiments this created unstable behavior when sending commands
def keep_drone_connection_alive():
    while True:
        try:
            send_command_to_drone('command')
            time.sleep(8)
        except:
            pass

