from paho.mqtt import client as mqtt_client
import random
import logging
import time
import threading
import json
import hashlib

import sensor

broker = 'rule28.i4t.swin.edu.au'
#broker = "broker.emqx.io"
port = 1883
client_id = f"python-mqtt-{random.randint(0, 1000)}"
username = "<103825154>"
password = "<103825154>"

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

topics = {
	"accelerometer": sensor.accelerometer,
	"temperature": sensor.temperature,
	"pressure": sensor.pressure,
	"strain": sensor.strain,
	"rotary_encoder": sensor.rotary_encoder
}

# When the client initiate connection
def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print("Connected to MQTT Broker")
	else:
		print("Failed to connect, return code %d\n", rc)

def on_message(client, userdata, msg):
	print("\n====================[SUB]====================")
	print(json.dumps({"topic": msg.topic, "qos": msg.qos, "retained": msg.retain, "message": msg.payload.decode()}, indent=4))
	print("=============================================")

# When the client signify end of connection
def on_disconnect(client, userdata, rc):
	logging.info("Disconnected with result code: %s", rc)
	reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
	while reconnect_count < MAX_RECONNECT_COUNT:
		logging.info("Reconnecting in %d seconds...", reconnect_delay)
		time.sleep(reconnect_delay)

		try:
			client.reconnect()
			logging.info("Reconnected successfully!")
			return
		except Exception as err:
			logging.error("%s. Reconnect failed. Retrying...", err)

		reconnect_delay *= RECONNECT_RATE
		reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
		reconnect_count += 1

	logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)

# use this function to initiate connection
def connect_mqtt():
	client = mqtt_client.Client(client_id)
	client.username_pw_set(username, password)
	client.on_connect = on_connect
	client.on_disconnect = on_disconnect
	client.on_message = on_message
	client.connect(broker, port)
	return client

def on_publish(client, sensor_name, sensor_func):
	while True:
		topic = f"<103825154>/sensors/{sensor_name}"
		sensor_data = sensor_func()
		message = {
			"data": sensor_data,
			"timestamp": time.time()
		}
		message_json = json.dumps(message)
		sha256_hash = hashlib.sha256(message_json.encode()).hexdigest()

		full_message = {
			"topic": topic,
			"hash": sha256_hash,
			"message": message,
		}
		full_message_json = json.dumps(full_message)

		result = client.publish(topic, full_message_json)
		time.sleep(1)


def publish(client):
	for sensor_name, sensor_func in topics.items():
		threading.Thread(target=on_publish, args=(client, sensor_name, sensor_func)).start()

def subscribe(client):
	client.subscribe("<103825154>/#")
	client.subscribe("public/#")

if __name__ == "__main__":
	client = connect_mqtt()

	try:
		subscribe(client)
		client.loop_start()
		publish(client)
	except KeyboardInterrupt:
		client.loop_stop()
		print("Terminate program")
