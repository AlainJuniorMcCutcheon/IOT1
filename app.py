import json
import time
import paho.mqtt.client as mqtt

# Unique ID matching the IoT device
id = "bdc80c7f-77ae-46c4-8015-ad7fa48f266a"  # Use the same ID from the IoT device
client_telemetry_topic = f"{id}/telemetry"
client_name = f"{id}_temperature_server"

# MQTT Setup
mqtt_client = mqtt.Client(client_name)
mqtt_client.connect("test.mosquitto.org")
mqtt_client.loop_start()

print("Server is listening for messages...")

def handle_telemetry(client, userdata, message):
    try:
        payload = json.loads(message.payload.decode())
        print("Message received:", payload)
    except json.JSONDecodeError:
        print("Error: Received invalid JSON data")

# Subscribe to temperature topic
mqtt_client.subscribe(client_telemetry_topic)
mqtt_client.on_message = handle_telemetry

# Keep server running
try:
    while True:
        time.sleep(2)
except KeyboardInterrupt:
    print("\nStopping server...")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    print("Server stopped.")
