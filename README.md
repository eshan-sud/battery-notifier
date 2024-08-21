# Battery Notifier

![icon](https://github.com/user-attachments/assets/98239ab1-1172-4a70-b703-ca9374c11da9)

**Battery Notifier** is a tool that helps you manage your battery usage by providing notifications based on battery levels, generating health reports, and toggling battery saver mode. Key features include:

- **Threshold Notifications**: Set minimum and maximum battery levels to receive notifications when thresholds are crossed.
- **Battery Health Report**: Generate a detailed report of your battery's health.
- **Battery Saver Toggle**: Enable or disable battery saver mode.
- **Monitoring Control**: Start and stop monitoring with ease.

## Setup

1. Open Command Prompt in the same directory as `setup.py`.
2. Execute: `python setup.py -y`

   This will create a shortcut on your desktop for easy access to the Battery Notifier interface and configure it to run automatically on startup (which can be adjusted as per user preference).

## Usage

- **Start Monitoring**: Click the "Start Monitoring" button to begin monitoring your battery levels.
- **Stop Monitoring**: Click the "Stop Monitoring" button to halt the monitoring process.
- **Generate Report**: Use the "Generate Battery Report" button to create a detailed battery health report.
- **Toggle Battery Saver**: Adjust battery saver settings as needed.
- **Save Settings**: Ensure your settings are saved and applied by clicking the "Save and Exit" button.

## Commands

- **`start`**: Starts the monitoring process.
- **`stop`**: Stops the monitoring process.
- **`report`**: Generates a battery health report.
- **`saver on`**: Enables battery saver mode.
- **`saver off`**: Disables battery saver mode.
- **`status`**: Shows the current status of monitoring and battery saver mode.

## Configuration

The application is configured via `settings.py`, which allows you to:

- **Create/Remove Startup Shortcut**: Add or remove a shortcut from the Windows Startup folder based on your preference.

**Note**: Ensure you have Python installed and added to your system PATH to use the setup and commands.
