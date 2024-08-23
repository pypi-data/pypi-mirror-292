import signal
import sys

def signal_handler(sig, frame):
    print("\nStop running!")
    sys.exit(0)

def config_signal():
    signal.signal(signal.SIGINT, signal_handler)