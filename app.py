import time
from datetime import datetime
import RPi.GPIO as GPIO
from seeed_dht import DHT
from grove.display.jhd1802 import JHD1802
from grove.grove_ultrasonic_ranger import GroveUltrasonicRanger
from grove.grove_light_sensor_v1_2 import GroveLightSensor
from influxdb import InfluxDBClient
from flask import Flask, render_template, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests



# InfluxDB Configuration
host = "localhost"       # InfluxDB server address
port = 8086              # Default port
username = "iot_final"   # Configured user
password = "iot_final"   # Configured password
database = "iot_data"    # Database name

client = InfluxDBClient(host=host, port=port, username=username, password=password, database=database)

# Flask Configuration
app = Flask(__name__)

# Sensor Configuration
GPIO.setmode(GPIO.BCM)
LIGHT_THRESHOLD = 10
SILENCE_THRESHOLD = 10
SOUND_SENSOR_PIN = 18
BUZZER_PIN = 16
PIR_PIN = 24
LED_PIN = 26  # Pin del LED

# GPIO inizializaztion
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.setup(SOUND_SENSOR_PIN, GPIO.IN)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)


class SensorSystem:
    def __init__(self):
        try:
            self.lcd = JHD1802()
            self.dht_sensor = DHT("11", 5)
            self.ultrasonic_sensor = GroveUltrasonicRanger(22)
            self.light_sensor = GroveLightSensor(0)
            self.silent_start_time = None

        except Exception as e:
            print(f"Error initializing sensors: {e}")
            self.lcd = None
            self.dht_sensor = None
            self.ultrasonic_sensor = None
            self.light_sensor = None

    def log_to_influx(self, measurement, fields):
            try:
                point = {
                    "measurement": measurement,
                    "fields": fields
                }
                client.write_points([point])
            except Exception as e:
              print(f"Error sending data to InfluxDB: {e}")

    def send_telegram_message(self,message):
        bot_token = "7588862093:AAGynDJjYtTk6jTkt-MM6QkU-fuct0CCDHs"
        chat_id = "7684370450"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": message
        }
        response = requests.post(url, data=params)


    def monitor_board_temperature(self):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                raw_temp = f.read().strip()
                temperature = int(raw_temp) / 1000.0
                self.log_to_influx("board_temperature", {"value": temperature})
                if temperature > 50:
                    GPIO.output(LED_PIN, True)
                else:
                    GPIO.output(LED_PIN, False)
        except Exception as e:
            print(f"Error monitoring board temperature: {e}")

    def get_greeting_message(self):
        current_hour = datetime.now().hour
        if 5 <= current_hour < 12:
            return "Good Moorning!!"
        elif 12 <= current_hour < 18:
            return "Good Afternoon!!"
        else:
            return "Good Night!!"

    def clear_lcd(self, message="", line=0):
        try:
            if self.lcd:
                self.lcd.clear()
                self.lcd.setCursor(line, 0)
                self.lcd.write(message)
        except Exception as e:
            print(f"Error writing to the LCD: {e}")

    def return_to_initial_state(self):
        greeting = self.get_greeting_message()
        self.clear_lcd(greeting, 0)

    def wait_for_light(self):
        try:
            self.clear_lcd("Waiting...", 0)
            while True:
                light_value = self.light_sensor.light if self.light_sensor else 0
                if light_value > LIGHT_THRESHOLD:
                    self.return_to_initial_state()
                    time.sleep(2)
                    break
                time.sleep(0.5)
        except Exception as e:
            print(f"Error detecting light: {e}")

    def check_silence(self):
        try:
            sound_detected = GPIO.input(SOUND_SENSOR_PIN)

            if sound_detected == 0:
                if self.silent_start_time is None:
                    self.silent_start_time = time.time()
                elif time.time() - self.silent_start_time >= SILENCE_THRESHOLD:
                    self.send_telegram_message( "Paco has been silent for a long time, why don't you call him and ask him how he is?"               )

                    self.clear_lcd("¿How are yoy?", 0)
                    self.activate_buzzer()

                    while GPIO.input(SOUND_SENSOR_PIN) == 0:
                        time.sleep(0.1)
                    self.clear_lcd("Nice!", 0)
                    time.sleep(2)
                    self.return_to_initial_state()
                    self.silent_start_time = None
            else:
                self.silent_start_time = None

        except Exception as e:
            print(f"Error monitoring silence: {e}")

    def activate_buzzer(self):
        try:
            GPIO.output(BUZZER_PIN, True)
            time.sleep(0.5)
            GPIO.output(BUZZER_PIN, False)
        except Exception as e:
            print(f"Error activating the buzzer: {e}")

    def display_temperature_humidity(self):
      try:
          if self.dht_sensor:
              humidity, temperature = self.dht_sensor.read()
              if humidity is not None and temperature is not None:
                  self.clear_lcd(f"Temp: {temperature:.1f}C", 0)
                  self.lcd.setCursor(1, 0)
                  self.lcd.write(f"Hum: {humidity:.1f}%")

                  self.log_to_influx("temperature", {"value": temperature})
                  self.log_to_influx("humidity", {"value": humidity})

                  time.sleep(3)
                  self.return_to_initial_state()
              else:
                  self.clear_lcd("Error DHT", 0)
      except Exception as e:
          print(f"Error reading DHT: {e}")

    def monitor_proximity(self):
        try:
            distance = self.ultrasonic_sensor.get_distance()
            if distance < 10:
                self.display_temperature_humidity()
        except Exception as e:
            print(f"Error checking proximity: {e}")

    def run(self):
        try:
            self.return_to_initial_state()
            while True:
                light_value = self.light_sensor.light if self.light_sensor else 0
                if light_value < LIGHT_THRESHOLD:
                    self.wait_for_light()
                    continue

                self.check_silence()
                self.monitor_proximity()
                self.monitor_board_temperature()
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Program interrupted. Cleaning GPIO.")
        except Exception as e:
            print(f"General error: {e}")
        finally:
            GPIO.cleanup()

# Rutas de Flask
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sensor_data')
def sensor_data():
    try:
        humidity, temperature = system.dht_sensor.read()
        sound_detected = GPIO.input(SOUND_SENSOR_PIN)
        data = {
            "temp": round(temperature, 1) if temperature else 0,
            "humid": round(humidity, 1) if humidity else 0,
            "sound": "Detected" if sound_detected else "Silent",
        }
        return jsonify(data)
    except Exception as e:
        print(f"Error reading sensors: {e}")
        return jsonify({"error": "Error reading sensors"}), 500


EMAIL_ADDRESS = "alexpelegrin10@gmail.com"
EMAIL_PASSWORD = "infj vebv lotr ibie"


def send_alert_email():
    recipient = "alexpelegrinzurdo@gmail.com"
    subject = "¡ALERT!"
    body = "An alert has been triggered."
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent.")
    except Exception as e:
        print(f"Error sending email: {e}")


@app.route('/alert', methods=['POST'])
def trigger_alert():
    send_alert_email()
    return "Alert triggered and email sent!", 200

import threading

if __name__ == "__main__":
    system = SensorSystem()

    monitoring_thread = threading.Thread(target=system.run, daemon=True)
    monitoring_thread.start()

    app.run(host='0.0.0.0', port=5000)
