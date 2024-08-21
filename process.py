# /process.py

import battery_utility
import multiprocessing
import time
import psutil
import os
import logger

def battery_process():
    """ Start monitoring battery events """
    battery_utility.monitor_battery_events()

def start_process():
    """ Create & start a separate process for monitoring the battery """
    parent_pid = os.getpid()
    logged_pids = logger.get_pids_from_log()
    if logged_pids and parent_pid not in logged_pids:
        logger.log_start_monitoring(parent_pid, "process.py (Parent Process)")    
    multiprocessing.set_start_method('spawn', force=True)
    process = multiprocessing.Process(target=battery_process, name="BatteryMonitorProcess")
    process.daemon = True
    process.start()
    if process.pid not in logged_pids:
        logger.log_start_monitoring(process.pid, "process.py (Child Process)")
    return process

def stop_process(process):
    """ Stops the monitoring process """
    try:
        if process:
            process.terminate()
            process.join()
            logger.log_stop_monitoring(process.pid, "process.py")
        else:
            logger.log_error("No active monitoring process found.", "process.py")
    except Exception as e:
        logger.log_error(f"Failed to stop monitoring: {e}", "process.py")

def stop_process_by_pid(pid):
    """ Stops a process using its PID """
    try:
        process = psutil.Process(pid)
        if process.is_running():
            process.terminate()
            process.wait()
            logger.log_stop_monitoring(process.pid, "process.py")
        else:
            logger.log_error("No active monitoring process found.", "process.py")
    except psutil.NoSuchProcess:
        logger.log_error(f"No process with PID {pid} found.", "process.py")
    except Exception as e:
        logger.log_error(f"Failed to stop monitoring: {e}", "process.py")

if __name__ == "__main__":
    """ Entry point for starting the monitor process """
    process = None
    try:
        process = start_process()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_process(process)
