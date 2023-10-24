import logging
import sys
import datetime
import os
from config import *

logger = None

def init():
    global logger
    if logger:
        return
    
    logger = logging.getLogger(__name__) 
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(original_file)s:%(original_line)d | %(message)s', '%Y-%m-%d %H:%M:%S')
    # formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s', '%Y-%m-%d %H:%M:%S')

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    current_date = datetime.date.today()
    formatted_date = current_date.strftime("%Y%m%d")

    if not os.path.exists(DEBUG_FOLDER):
        os.makedirs(DEBUG_FOLDER)

    rotate_debug_files()

    argv0 = sys.argv[0].split('/')
    debug_file = argv0[len(argv0) - 1][0:-3] + "_" + formatted_date + ".log"
    fileHandler = logging.FileHandler(os.path.join(DEBUG_FOLDER, debug_file), 'w+')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

def rotate_debug_files(directory_path=DEBUG_FOLDER):
    threshold_date = datetime.date.today() - datetime.timedelta(days=DEBUG_FILE_DAYS_THRESHOLD)

    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        if os.path.isfile(file_path):
            modification_time = datetime.date.fromtimestamp(os.path.getmtime(file_path))

            if modification_time < threshold_date:
                os.remove(file_path)

def _pre_debug():
    frame = sys._getframe(2)    # use 2 because _pre_debug() is 0, 
    filename = os.path.basename(frame.f_code.co_filename)
    print(filename)
    lineno = frame.f_lineno
    return {'original_file': filename, 'original_line': lineno}

def debug(str):
    # if not logger:
    #     init()

    logger.debug(str, extra=_pre_debug())

def info(str):
    if not logger:
        init()
    
    logger.info(str, extra=_pre_debug())

def warn(str):
    if not logger:
        init()
    logger.warn(str, extra=_pre_debug())

def error(str):
    if not logger:
        init()
    logger.error(str, extra=_pre_debug())

def critical(str):
    if not logger:
        init()
    logger.critical(str, extra=_pre_debug())