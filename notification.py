# /notification.py

import os
from plyer import notification
import battery_utility

def notify_user(percentage, lower_threshold, higher_threshold, power_plugged):
    """ Notify when battery is fully charged or low based on thresholds """
    if power_plugged and percentage >= higher_threshold:
        message = f"Battery is charged to {percentage}%. Please unplug the charger."
        notification_message(message)
    elif not power_plugged and percentage <= lower_threshold:
        message = f"Battery is at {percentage}%. Consider plugging in."
        battery_utility.toggle_battery_saver()
        notification_message(message)

def notification_message(message, title="Battery Notification", timeout=5):
    """ Send a desktop notification with the given message """
    icon_path = os.path.abspath("images/icon.ico")
    notification.notify(
        title=title,
        message=message,
        timeout=timeout,
        app_icon=icon_path
    )
