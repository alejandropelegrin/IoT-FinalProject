# IoT Sensor Dashboard for Elderly Care

This project is an IoT system designed to mitigate loneliness in elderly individuals while ensuring their safety. The system monitors various environmental factors such as temperature, humidity, light, and sound, and provides real-time alerts and notifications in case of unusual activity.

## Features
- *Elderly Care*:
  - Detects extended periods of silence and sends reminders or notifications to check in on the user.
  - Displays messages on an LCD to interact with the user.
- *Safety Monitoring*:
  - Monitors temperature, humidity, light, and proximity to ensure a safe environment.
  - Alerts caregivers via Telegram and email in emergencies.
- *User-Friendly Dashboard*:
  - A web-based dashboard to view real-time sensor data and trigger manual alerts.

## Technologies Used
- *Backend*: Flask (Python).
- *Frontend*: HTML and CSS.
- *Database*: InfluxDB.
- *Hardware*:
  - Sensors: DHT11 for temperature and humidity, ultrasonic for proximity, red led buttom, and light and sound sensors.
  - Raspberry Pi GPIO for managing sensors and actuators.
  - LCD

## Installation
### Prerequisites
- Raspberry Pi with Raspbian OS.
- Python 3.x installed.
- Required dependencies:
  ```bash
  pip install flask RPi.GPIO influxdb grove.py
