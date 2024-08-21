# /setup.py

import os
import sys
import subprocess
from win32com.client import Dispatch

def install_requirements():
    """ Installs the Python packages listed in requirements.txt """
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("Packages installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")

def create_shortcut(script_path, shortcut_path, icon_path):
    """ Creates a shortcut to the target executable """
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortcut(shortcut_path)
    shortcut.TargetPath = sys.executable.replace("python.exe", "pythonw.exe")
    shortcut.Arguments = f'"{script_path}"'
    shortcut.WorkingDirectory = os.path.dirname(script_path)
    shortcut.IconLocation = icon_path
    shortcut.save()
    print("Shortcut Created")

if __name__ == "__main__":

    install_requirements()

    desktop_folder = os.path.join(os.getenv('USERPROFILE'), 'Desktop')
    script = os.path.abspath("settings.py")
    shortcut_file = os.path.join(desktop_folder, "Battery Notifier Settings.lnk")
    icon_file = os.path.abspath("images/icon.ico")
    create_shortcut(script, shortcut_file, icon_file)
