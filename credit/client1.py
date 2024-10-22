from paho.mqtt import client as mqtt_client
import random
import logging
import time
import threading
import json
import hashlib

import sensor

broker = 'rule28.i4t.swin.edu.au'
port = 1883
client_id = f"python-mqtt-{random.randint(0, 1000)}"
username = "<103825154>"
password = "<103825154>"

# list of sensor topics with their respective functions
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

# Receive messages from subscribed topics
# Print out message content, topic, qos and retain
def on_message(client, userdata, msg):
	print("\n====================[SUB]====================")
	print(json.dumps({"topic": msg.topic, "qos": msg.qos, "retained": msg.retain, "message": msg.payload.decode()}, indent=4))
	print("=============================================")

# use this function to initiate connection
def connect_mqtt():
	client = mqtt_client.Client(client_id)
	client.username_pw_set(username, password)
	client.on_connect = on_connect
	client.on_message = on_message
	client.connect(broker, port)
	return client

# publish function on a single sensor
def on_publish(client, sensor_name, sensor_func):
	while True:
		topic = f"<103825154>/sensors/{sensor_name}"
		# get sensor reading from sensor_func call back
		sensor_data = sensor_func()
		# define message content, consists of sensor reading and current timestamp
		message = {
			"data": sensor_data,
			"timestamp": time.time()
		}
		message_json = json.dumps(message)
		sha256_hash = hashlib.sha256(message_json.encode()).hexdigest()

		# full message consists of message content, topic name and sha256 checksum from mssage content
		full_message = {
			"topic": topic,
			"hash": sha256_hash,
			"message": message,
		}
		full_message_json = json.dumps(full_message)
		# publish the json encoded data to the topic
		result = client.publish(topic, full_message_json)
		# rest for one second
		time.sleep(1)

# publishing multiple sensors readings concurrently using multithread
def publish(client):
	for sensor_name, sensor_func in topics.items():
		threading.Thread(target=on_publish, args=(client, sensor_name, sensor_func)).start()

# subscribe to private and public topics
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
