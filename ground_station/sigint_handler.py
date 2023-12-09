import signal

shutdown_signal = False

def signal_handler(signum, frame):
    print(f'SIGINT received at "{frame.f_code.co_name}" with signal {signum}')
    global shutdown_signal
    shutdown_signal = True

signal.signal(signal.SIGINT, signal_handler)
