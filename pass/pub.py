from paho.mqtt import client as mqtt_client
import random
import logging
import time

# BROKER CONNECTION INFORMATION
broker = 'rule28.i4t.swin.edu.au' # Server name
port = 1883 # port number
client_id = f"python-mqtt-{random.randint(0, 1000)}" # Client id
username = "<103825154>" # Username
password = "<103825154>" # Password

# Reconnection constants
FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

# When the client initiate connection
def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print("Connected to MQTT Broker")
	else:
		print("Failed to connect, return code %d\n", rc)

# When the client signifies end of connection
# Auto reconnect upon disconnect for MAX_RECONNECT_COUNT times
# each reconnect count will attempt to reconnect in FIRST_RECONNECT_DELAY
# then reconnect delay will double after each count
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
	client.connect(broker, port)
	return client

topic_temperature = "<103825154>/temperature"

# Dummy function for temperature topic
# This function publish a temperature message with random value
def publish_temperature(client, topic_name):
	while True:
		try:
			time.sleep(1)
			temp = random.randint(-10,100)
			msg = f"temperature: {temp} \u2103"
			result = client.publish(topic_name, msg)
			status = result[0]
			if status == 0:
				print(f"Send `{msg}` to topic `{topic_name}`")
			else:
				print(f"Failed to send message to topic {topic_name}")
		except KeyboardInterrupt:
			print("Terminate program")
			break

if __name__ == "__main__":
	# 1. Initiate connection
	client = connect_mqtt()
	client.loop_start()

	publish_temperature(client, topic_temperature)

	client.loop_stop()
