# IoT Sensor Dashboard for Elderly Care

This project is an IoT system designed to mitigate loneliness in elderly individuals while ensuring their safety. The system monitors various environmental factors such as temperature, humidity, light, and sound, and provides real-time alerts and notifications in case of unusual activity.

## Features
- *Elderly Care*:
  - Detects extended periods of silence and sends reminders or notifications to caregivers, encouraging them to check in on the user.
  - Displays greeting messages and reminders on an LCD to interact with the user and promote engagement.
- *Safety Monitoring*:
  - Continuously monitors:
    - *Temperature* and *Humidity*: Ensures a safe environment by tracking environmental conditions.
    - *Light Levels*: Waits for sufficient light before activating features, as it assumes that the presence of light indicates someone is likely at home or actively using the space.
    - *Sound Levels*: Detects prolonged silence and triggers alerts.
    - *Proximity*: When a user approaches, the system displays the current temperature and humidity on the LCD.
  - Alerts caregivers via *Telegram* and *email* in emergencies.
  - Activates visual or audible warnings (e.g., LED or buzzer) when thresholds are exceeded.
- *User-Friendly Dashboard*:
  - A web-based dashboard allows caregivers to:
    - View real-time sensor data, including temperature, humidity, and sound levels.
    - Trigger manual alerts directly from the interface.

## Technologies Used
- *Backend*: Flask (Python).
- *Frontend*: HTML, CSS, and JavaScript.
- *Database*: InfluxDB for storing sensor data.
- *Hardware*:
  - *Sensors*:
    - DHT11: Measures temperature and humidity.
    - Ultrasonic: Detects proximity for interactive feedback.
    - Light sensor: Monitors ambient light levels.
    - Sound sensor: Detects noise and silence.
  - *Actuators*:
    - LED and buzzer: Provide visual and audible alerts.
  - *LCD Display*: Displays sensor readings and greeting messages.
  - Raspberry Pi GPIO: Manages sensor and actuator connections.

## Installation
### Prerequisites
- Raspberry Pi with Raspbian OS.
- Python 3.x installed.
- Required dependencies:
  ```bash
  pip install flask RPi.GPIO influxdb grove.py

## Steps
### 1. Clone this repository
### 2. Configure the app.py file with your InfluxDB and Telegram credentials.
### 3. Start the Flask server:
  ```bash
  python3 app.py

