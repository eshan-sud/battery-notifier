# /settings.py

import os
import sys
import json
import tkinter as tk
from tkinter import messagebox
from win32com.client import Dispatch
import subprocess
import psutil
import ctypes
import threading

import process
import battery_utility
from logger import log_start_monitoring, log_stop_monitoring, log_error, get_pids_from_log, get_last_record_from_log

# File paths for config file & process script file
CONFIG_FILE_PATH = "./config.json"

def load_config():
    """ Load & return user configuration """
    DEFAULT_CONFIG = {
        "lower_threshold": 20,
        "higher_threshold": 80,
        "startup": False,
        "dark_mode": False,
        "batter_saver_on": battery_utility.is_battery_saver_on(),
        "current_brightness": battery_utility.get_brightness()
    }
    try:
        if os.path.exists(CONFIG_FILE_PATH):
            with open(CONFIG_FILE_PATH, 'r') as config_file:
                content = config_file.read().strip()
                if content:
                    return json.loads(content)
                else:
                    raise ValueError("Config file is empty")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load configuration file. Resetting to defaults...\nError: {e}")
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config):
    """ Saves the user configuration to the config file """
    try:
        with open(CONFIG_FILE_PATH, 'w') as config_file:
            json.dump(config, config_file, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save configuration: {e}")

def generate_battery_report():
    """ Generates & stores the battery health report to desktop """
    try:
        # Get the path to user's desktop
        desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        report_path = os.path.join(desktop_path, 'battery_report.html')
        # Generate battery report & save it to the desktop
        subprocess.run(f"powercfg /batteryreport /output \"{report_path}\"", shell=True, check=True)
        messagebox.showinfo("Report Generated", f"Battery report has been saved to {report_path}")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to generate battery report.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def set_startup(is_startup):
    """ Manages the startup behavior """
    try:
        startup_path = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        shortcut_path = os.path.join(startup_path, "Battery Notifier.lnk")
        script_path = os.path.abspath("process.py")
        icon_path = os.path.abspath("images/icon.ico")

        if is_startup:
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortcut(shortcut_path)
            shortcut.TargetPath = sys.executable.replace("python.exe", "pythonw.exe")
            shortcut.Arguments = f'"{script_path}"'
            shortcut.WorkingDirectory = os.path.dirname(script_path)
            shortcut.IconLocation = icon_path
            shortcut.save()  # Create startup shortcut
        else:
            if os.path.exists(shortcut_path):
                os.remove(shortcut_path)  # Remove startup shortcut
    except Exception as e:
        messagebox.showerror("Error", f"Failed to manage startup settings: {e}")

def set_title_bar_color(hwnd, is_dark_mode):
    """ Sets the title bar color based on dark mode setting """
    try:
        DWMWA_USE_IMMERSIVE_DARK_MODE = 20
        color = 1 if is_dark_mode else 0
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE, ctypes.byref(ctypes.c_int(color)), ctypes.sizeof(ctypes.c_int(color))
        )
    except Exception as e:
        messagebox.showerror("Error", f"Failed to set title bar color: {e}")

def toggle_dark_mode(window, dark_mode_var, checkbuttons):
    """ Toggles Dark Mode Setting """
    is_dark_mode = dark_mode_var.get()  # Get the current dark mode setting
    hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
    try:
        # Dark mode settings
        if is_dark_mode:
            window.config(bg='black')
            set_title_bar_color(hwnd, True)
            for widget in window.winfo_children():
                if isinstance(widget, tk.Canvas):
                    widget.config(bg='black')
                elif isinstance(widget, tk.Entry):
                    widget.config(bg='black', fg='white', insertbackground='white')
                else:
                    widget.config(bg='black', fg='white')
            for cb in checkbuttons:
                cb.config(bg='black', fg='white', selectcolor='black')
        # Light mode settings
        else:
            window.config(bg='white')
            set_title_bar_color(hwnd, False)
            for widget in window.winfo_children():
                if isinstance(widget, tk.Canvas):
                    widget.config(bg='white')
                elif isinstance(widget, tk.Entry):
                    widget.config(bg='white', fg='black', insertbackground='black')
                else:
                    widget.config(bg='white', fg='black')
            for cb in checkbuttons:
                cb.config(bg='white', fg='black', selectcolor='white')
        
        # Update battery level display
        battery = psutil.sensors_battery()
        battery_level = battery.percent if battery else 0
        battery_canvas = window.winfo_children()[0]
        update_battery_level(battery_canvas, battery_level)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to toggle dark mode: {e}")

def save_and_exit(lower_threshold_var, higher_threshold_var, startup_var, dark_mode_var, window):
    """ Save the user's settings & exit the settings application (Not the monitoring process) """
    try:
        config = {
            "lower_threshold": lower_threshold_var.get(),
            "higher_threshold": higher_threshold_var.get(),
            "startup": startup_var.get() == 1,
            "dark_mode": dark_mode_var.get() == 1,
            "battery_saver_on": battery_utility.is_battery_saver_on(),
            "current_brightness": battery_utility.get_brightness(),
        }
        save_config(config)
        set_startup(config["startup"])
        messagebox.showinfo("Settings Saved", "Your settings have been saved.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save settings: {e}")
    finally:
        window.quit()

def update_battery_level(canvas, battery_level):
    """ Updates the battery level displayed on the canvas """
    try:
        if isinstance(canvas, tk.Canvas):
            canvas.delete("battery")
            width = 210
            height = 30
            fill_width = (battery_level / 100) * width    
            bg_color = canvas["bg"]
            outline_color = text_color = "white" if bg_color == "black" else "black"
            fill_color = "green"
            canvas.create_rectangle(5, 5, width, height + 5)
            canvas.create_rectangle(5, 5, fill_width, height + 5, fill=fill_color, tags="battery")    
            canvas.create_text(width / 2 + 5, height / 2 + 5, text=f"{battery_level}%", fill=text_color, tags="battery")
        else:
            raise TypeError("Provided widget is not a Canvas")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update battery level: {e}")

def start_monitoring():
    """ Starts the monitoring process """
    try:
        last_record = get_last_record_from_log()
        if last_record:
            if "Start monitoring process initiated" in last_record:
                messagebox.showinfo("Info", "Monitoring is already running.")
                return
        script_path = os.path.abspath("process.py")
        process = subprocess.Popen([sys.executable, script_path], creationflags=subprocess.CREATE_NO_WINDOW)
        log_start_monitoring(process.pid, "settings.py")
        messagebox.showinfo("Info", "Monitoring started successfully.")
    except Exception as e:
        log_error(f"Failed to start monitoring: {e}", "settings.py")
        messagebox.showerror("Error", f"Failed to start monitoring: {e}")

def stop_monitoring():
    """ Stops the monitoring process """
    try:
        pids = get_pids_from_log()
        if pids:
            if len(pids) == 2:
                pid1, pid2 = pids
                process.stop_process_by_pid(pid1)
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['pid'] == pid2 and (proc.info['name'] == 'python.exe' or proc.info['name'] == "pythonw.exe"):
                        proc.terminate()
                        proc.wait()
                        log_stop_monitoring(pid2, "settings.py")
                        messagebox.showinfo("Info", "Monitoring stopped successfully.")
                        break
                else:
                    messagebox.showwarning("Warning", "Monitoring process not found.")
            else:
                process.stop_process_by_pid(pids[0])
                messagebox.showinfo("Info", "Monitoring stopped successfully.")
        else:
            messagebox.showwarning("Warning", "No monitoring process found.")
    except Exception as e:
        log_error(f"Failed to stop monitoring: {e}", "settings.py")
        messagebox.showerror("Error", f"Failed to stop monitoring: {e}")

def center_window(window):
    """ Centers the window to the screen """
    try:
        window.update_idletasks()
        window_width = window.winfo_width()
        window_height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        window.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")
        return window
    except Exception as e:
        messagebox.showerror("Error", f"Failed to center window: {e}")

def create_settings_window():
    """ Creates & shows the settings window """
    try:
        config = load_config()

        window = tk.Tk()
        window.title("Battery Notifier")
        window.geometry("350x450")
        window.resizable(False, False)
        center_window(window)

        padding_options = {'padx': 10, 'pady': 10}

        # Create a canvas to display the battery level
        battery_canvas = tk.Canvas(window, width=210, height=30, bg="lightgrey", borderwidth=2, relief="solid")
        battery_canvas.grid(row=0, column=0, columnspan=2, rowspan=1)

        battery_canvas.grid_rowconfigure(0, weight=1)
        battery_canvas.grid_columnconfigure(0, weight=1)

        battery = psutil.sensors_battery()
        battery_level = battery.percent if battery else 0
        update_battery_level(battery_canvas, battery_level)

        # Create checkboxes for setting the script as a startup process and toggling dark mode
        startup_var = tk.IntVar(value=config.get('startup', 0))
        startup_checkbutton = tk.Checkbutton(window, text="Run on startup", variable=startup_var, font=("Arial", 10))
        startup_checkbutton.grid(row=1, column=0, columnspan=3, **padding_options)

        dark_mode_var = tk.IntVar(value=config.get('dark_mode', 0))
        dark_mode_checkbutton = tk.Checkbutton(window, text="Dark Mode", variable=dark_mode_var, font=("Arial", 10), command=lambda: toggle_dark_mode(window, dark_mode_var, [startup_checkbutton, dark_mode_checkbutton]))
        dark_mode_checkbutton.grid(row=2, column=0, columnspan=3, **padding_options)

        # Create spinboxes for setting lower and higher battery thresholds
        tk.Label(window, text="Lower Threshold (%)", font=("Arial", 10)).grid(row=3, column=0, **padding_options, sticky="w")
        lower_threshold_var = tk.IntVar(value=config['lower_threshold'])
        lower_threshold_spinbox = tk.Spinbox(window, from_=1, to=99, textvariable=lower_threshold_var, font=("Arial", 10))
        lower_threshold_spinbox.grid(row=3, column=1, **padding_options, sticky="ew")

        tk.Label(window, text="Higher Threshold (%)", font=("Arial", 10)).grid(row=4, column=0, **padding_options, sticky="w")
        higher_threshold_var = tk.IntVar(value=config['higher_threshold'])
        higher_threshold_spinbox = tk.Spinbox(window, from_=1, to=99, textvariable=higher_threshold_var, font=("Arial", 10))
        higher_threshold_spinbox.grid(row=4, column=1, **padding_options, sticky="ew")

        tk.Button(window, text="Generate Battery Report", command=generate_battery_report, font=("Arial", 10)).grid(row=5, column=0, columnspan=3, **padding_options)
        tk.Button(window, text="Start Monitoring", command=lambda: threading.Thread(target=start_monitoring).start(), font=("Arial", 10)).grid(row=6, column=0, **padding_options)
        tk.Button(window, text="Stop Monitoring", command=lambda: threading.Thread(target=stop_monitoring).start(), font=("Arial", 10)).grid(row=6, column=1, **padding_options)
        tk.Button(window, text="Toggle Battery Saver", command=battery_utility.toggle_battery_saver, font=("Arial", 10)).grid(row=7, column=0, columnspan=3, **padding_options)
        tk.Button(window, text="Save and Exit", command=lambda: save_and_exit(lower_threshold_var, higher_threshold_var, startup_var, dark_mode_var, window), font=("Arial", 10)).grid(row=8, column=0, columnspan=3, **padding_options)

        window.grid_columnconfigure(0, weight=1)
        window.grid_columnconfigure(1, weight=1)
        window.grid_columnconfigure(2, weight=1)

        window.update_idletasks()
        
        # Manage window title bar color based on dark mode setting
        toggle_dark_mode(window, dark_mode_var, [startup_checkbutton, dark_mode_checkbutton])

        window.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    """ Entry point for starting the monitor process """
    try:
        create_settings_window()
    except KeyboardInterrupt:
        print("Exited ...")
    except Exception as e:
        print(e)
