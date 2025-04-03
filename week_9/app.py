import json
import time
import paho.mqtt.client as mqtt

# Unique ID for MQTT topics
id = "bdc80c7f-77ae-46c4-8015-ad7fa48f266a"
client_telemetry_topic = f"{id}/telemetry"
server_command_topic = f"{id}/commands"  # Topic for sending commands
client_name = f"{id}_temperature_server"

# MQTT Setup
mqtt_client = mqtt.Client(client_name)
mqtt_client.connect("test.mosquitto.org")
mqtt_client.loop_start()

def handle_telemetry(client, userdata, message):
    """Handles incoming temperature data and sends LED commands."""
    payload = json.loads(message.payload.decode())
    print("Message received:", payload)

    temp = payload.get("temperature")
    if temp is not None:
        command = {"led_on": temp > 27}  # Turn LED on if temp > 25
        print("Sending command:", command)
        mqtt_client.publish(server_command_topic, json.dumps(command))

mqtt_client.subscribe(client_telemetry_topic)
mqtt_client.on_message = handle_telemetry

print("Server is listening for temperature data...")

while True:
    time.sleep(2)  # Keep the script running
