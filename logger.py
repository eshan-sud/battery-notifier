# /logger.py

import logging
import os
import re

# Define the log path and directory
LOG_DIR = "./logs"
LOG_PATH = os.path.join(LOG_DIR, "battery_monitoring.log")

# Create the log directory if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure logging
logging.basicConfig(filename=LOG_PATH, level=logging.INFO, format='%(asctime)s - %(message)s')

def log_start_monitoring(pid, caller):
    """ Logs the start of the monitoring process with PID """
    logging.info(f"Start monitoring process initiated (caller = {caller}) with PID: {pid}")

def log_stop_monitoring(pid, caller):
    """ Logs the stop of the monitoring process with PID """
    logging.info(f"Stop monitoring process initiated (caller = {caller}) with PID: {pid}")

def log_error(message, caller):
    """ Logs an error message """
    logging.error(f"Error (caller = {caller})): {message}")

def get_pids_from_log():
    """ Retrieves the last two logged PIDs from the log file that correspond to 'start' actions """
    pids = []
    try:
        with open(LOG_PATH, 'r') as log_file:
            lines = log_file.readlines()
            for line in reversed(lines):
                if 'Start monitoring process initiated' in line:
                    match = re.search(r'PID.*:\s*(\d+)', line)
                    if match:
                        try:
                            pid = int(match.group(1))
                            pids.append(pid)
                        except ValueError:
                            log_error(f"Invalid PID format in log line: {line.strip()}", "logger.py")
                if len(pids) == 2:
                    return pids
    except Exception as e:
        log_error(f"Failed to retrieve PIDs from log: {e}", "logger.py")
    return pids if pids else None

def get_last_record_from_log():
    """ Retrieves the last record from the log file """
    try:
        with open(LOG_PATH, 'r') as log_file:
            lines = log_file.readlines()
            if lines:
                last_record = lines[-1].strip()
                return last_record
            else:
                return None
    except Exception as e:
        log_error(f"Failed to retrieve last record from log: {e}")
        return None