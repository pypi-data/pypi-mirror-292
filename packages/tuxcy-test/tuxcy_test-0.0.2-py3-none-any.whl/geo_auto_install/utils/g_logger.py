from geo_auto_install.utils.g_common import *
from geo_auto_install.utils.g_fs import *
import os
import sys
import datetime

class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    YELLOW_UNDERLINE = '\033[4;33m'
    DARKCYAN_UNDERLINE = '\033[4;36m'
    END = '\033[0m'

class Logger:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, context):
        if self._initialized:
            return
        self._initialized = True
        self.log_file_path = None
        self.init_logger(context)

    def init_logger(self, context):
        log_file_dest = context[CTX_PROP_LOG_DEST]

        current_date_time = datetime.datetime.now().strftime("%d-%m-%Y-%H:%M")
        log_file_name = "update-{}.log".format(current_date_time)
        self.log_file_path = os.path.join(log_file_dest, log_file_name)

        if not os.path.exists(log_file_dest):
            os.makedirs(log_file_dest)

        file = open(self.log_file_path, "w")
        file.close()

    def log(self, message, color=Color.END):
        message = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S - ') + message
        safe_append(self.log_file_path, message)
        print(color + message + Color.END)

def log(message, color=Color.END):
    logger = Logger(None)
    
    if logger.log_file_path is None:
        print("Logger is not init.")
        sys.exit(1)

    logger.log(message, color)