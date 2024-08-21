# /battery_utility.py

import json
import psutil
import notification
import settings
import threading
import subprocess
import wmi
from tkinter import messagebox

from logger import log_error

# Brightness level at low battery or battery saving mode 
LOWER_BRIGHTNESS_VALUE = 30
# Power scheme GUIDs
BALANCED_GUID = "a1841308-3541-4fab-bc81-f71556f20b4a"
POWER_SAVER_GUID = "381b4222-f694-41f0-9685-ff5bb260df2e"

def monitor_battery_events():
    """ Monitors battery events such as plug in or plug out charging """
    last_power_plugged = None
    while True:
        try:
            config = settings.load_config()
            lower_threshold, higher_threshold = config['lower_threshold'], config['higher_threshold']
            battery = psutil.sensors_battery()

            if battery is None:
                log_error("Cannot access battery information.")
                break

            percentage, power_plugged = battery.percent, battery.power_plugged

            if last_power_plugged is None or power_plugged != last_power_plugged:
                if power_plugged:
                    notification.notification_message("Charging cable plugged in.")
                else:
                    notification.notification_message("Charging cable unplugged.")
                
                if power_plugged and percentage >= higher_threshold:
                    notification.notification_message(f"Battery is charged to {percentage}%. Please unplug the charger.")
                elif not power_plugged and percentage <= lower_threshold:
                    notification.notification_message(f"Battery is at {percentage}%. Consider plugging in.")
                last_power_plugged = power_plugged

        except Exception as e:
            log_error(f"Error in monitor_battery_events: {e}")
        
        # Wait for a second before checking again
        threading.Event().wait(1)

# def monitor_battery_events():
#     """ Monitors battery events such as plug in or plug out charging """
#     last_power_plugged = psutil.sensors_battery().power_plugged
#     while True:
#         try:
#             config = settings.load_config()
#             lower_threshold, higher_threshold = config['lower_threshold'], config['higher_threshold']
#             battery = psutil.sensors_battery()
#             if battery is None:
#                 log_error(f"Cannot access battery information.")
#                 break
#             percentage, power_plugged = battery.percent, battery.power_plugged
#             # Detect changes in power source (plugged in or unplugged)
#             if last_power_plugged is None or power_plugged != last_power_plugged:
#                 if power_plugged:
#                     notification.notification_message("Charging cable plugged in.")
#                     if percentage >= higher_threshold:
#                         notification.notification_message(f"Battery is charged to {percentage}%. Please unplug the charger.")
#                 else:
#                     notification.notification_message("Charging cable unplugged.")
#                     if percentage <= lower_threshold:
#                         notification.notification_message(f"Battery is at {percentage}%. Consider plugging in.")
#                 last_power_plugged = power_plugged
#         except Exception as e:
#             log_error(f"Error in monitor_battery_events: {e}")
#         finally:
#             threading.Event().wait(1)

def get_brightness():
    """ Returns the current screen brightness level (0-100) """
    try:
        wmi_service = wmi.WMI(namespace='wmi')
        brightness_methods = wmi_service.WmiMonitorBrightness()[0]
        return brightness_methods.CurrentBrightness
    except Exception as e:
        messagebox.showerror("Error", f"Failed to get brightness: {e}")
    return None

def set_brightness(level):
    """ Adjusts screen brightness to the given level (0-100) """
    try:
        wmi_service = wmi.WMI(namespace='wmi')
        brightness_methods = wmi_service.WmiMonitorBrightnessMethods()[0]
        brightness_methods.WmiSetBrightness(level, 0)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to adjust brightness: {e}")

def get_active_power_scheme():
    """ Returns the GUID of the currently Active power scheme """
    try:
        result = subprocess.run("powercfg /getactivescheme", shell=True, capture_output=True, text=True, check=True)
        active_scheme = result.stdout.split(":")[1].strip().split()[0]
        return active_scheme
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to retrieve active power scheme: {e}\n{e.stderr}")
    return None

def activate_battery_saver():
    """ Activates battery saver mode by switching to Power Saver plan """
    try:
        active_scheme = get_active_power_scheme()
        if active_scheme == POWER_SAVER_GUID:
            messagebox.showinfo("Battery Saver", "Battery Saver is already active.")
            return

        current_brightness = get_brightness()
        config = settings.load_config()
        config['saved_brightness'] = current_brightness
        settings.save_config(config)

        if current_brightness > LOWER_BRIGHTNESS_VALUE:
            set_brightness(LOWER_BRIGHTNESS_VALUE)

        subprocess.run(f"powercfg.exe /setactive {POWER_SAVER_GUID}", shell=True, check=True, capture_output=True, text=True)
        messagebox.showinfo("Battery Saver", "Battery Saver mode activated successfully.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to activate Battery Saver: {e}\n{e.stderr}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save brightness level: {e}")

def deactivate_battery_saver():
    """ Deactivates battery saver mode by switching to Balanced plan """
    try:
        active_scheme = get_active_power_scheme()
        if active_scheme == BALANCED_GUID:
            messagebox.showinfo("Battery Saver", "Balanced plan is already active.")
            return
        subprocess.run(f"powercfg.exe /setactive {BALANCED_GUID}", shell=True, check=True, capture_output=True, text=True)
        config = settings.load_config()
        saved_brightness = config.get('saved_brightness', 50)
        set_brightness(saved_brightness)
        messagebox.showinfo("Battery Saver", "Battery Saver mode deactivated, Balanced plan activated.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Failed to deactivate Battery Saver: {e}\n{e.stderr}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to restore brightness level: {e}")

def toggle_battery_saver():
    """ Toggles the battery saver mode based on the current state """
    if is_battery_saver_on():
        deactivate_battery_saver()
    else:
        activate_battery_saver()

def is_battery_saver_on():
    """ Checks whether the battery saver mode is currently on """
    try:
        return get_active_power_scheme() == POWER_SAVER_GUID
    except subprocess.CalledProcessError as e:
        log_error(f"Failed to check battery saver status: {e}")
        return False
