import os
import glob
import time
import json
import paho.mqtt.client as mqtt
from gpiozero import LED

# LED setup
red = LED(17)

# Unique MQTT ID
id = "bdc80c7f-77ae-46c4-8015-ad7fa48f266a" 
client_name = id + "temperature_client"
client_telemetry_topic = f"{id}/telemetry"  # MQTT topic for telemetry

# MQTT Setup
mqtt_client = mqtt.Client(client_name)
mqtt_client.connect("test.mosquitto.org")
mqtt_client.loop_start()

print("MQTT connected!")


def setup():
    """Initialize the DS18B20 sensor and return the device file path."""
    os.system("modprobe w1-gpio")
    os.system("modprobe w1-therm")
    base_dir = "/sys/bus/w1/devices/"
    device_folder = glob.glob(base_dir + "28*")[0]
    device_file = device_folder + "/w1_slave"
    return device_file


def read_file(device_file):
    """Read raw data from the sensor file."""
    try:
        with open(device_file, "r") as f:
            lines = f.readlines()
        return lines
    except FileNotFoundError:
        print("Error: Device file not found.")
        return []


def read_temperature(device_file):
    """Extract temperature value from the DS18B20 sensor data."""
    lines = read_file(device_file)
    if not lines:
        print("Error: No data to read from the sensor.")
        return None

    while lines[0].strip()[-3:] != "YES":
        time.sleep(0.1)  # Wait for the sensor to stabilize
        lines = read_file(device_file)

    try:
        temp_string = lines[1].split("t=")[-1]
        temp_celsius = float(temp_string) / 1000.0
        return round(temp_celsius, 2)
    except IndexError:
        print("Error: Index error while parsing temperature data.")
        return None


def loop():
    """Main loop to read temperature, control LED, and publish JSON telemetry."""
    device_file = setup()
    while True:
        temp_celsius = read_temperature(device_file)
        if temp_celsius is not None:
            print(f"Temperature: {temp_celsius}°C")

            # Control LED based on temperature
            if temp_celsius > 25:
                red.on()
            else:
                red.off()

            # Publish telemetry as JSON
            telemetry_data = {"temperature": temp_celsius}
            mqtt_client.publish(client_telemetry_topic, json.dumps(telemetry_data))

        time.sleep(3)  # Read every 3 seconds


if __name__ == "__main__":
    print("Press Ctrl+C to stop the program...")
    try:
        loop()
    except KeyboardInterrupt:
        print("\nStopping...")
        red.off()
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
        print("Goodbye!")