from paho.mqtt import client as mqtt_client
import random
import logging
import time
import threading

# broker = 'rule28.i4t.swin.edu.au'
broker = "broker.emqx.io"
port = 1883
client_id = f"python-mqtt-{random.randint(0, 1000)}"
#username = "<103825154>"
#password = "<103825154>"

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
	#client.username_pw_set(username, password)
	client.on_connect = on_connect
	client.on_disconnect = on_disconnect
	client.connect(broker, port)
	return client

# We have two topics for now
topic_temperature = "<103825154>/temperature"
topic_humidity = "<103825154>/humidity"

# Dummy function for temperature topic
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

# Dummy function for humidity topic
def publish_humidity(client, topic_name):
	while True:
		try:
			time.sleep(2)
			humid = random.randint(0,100)
			msg = f"humidity: {humid}%"
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
	client = connect_mqtt()
	client.loop_start()

	threading.Thread(target=publish_temperature, args=(client, topic_temperature)).start()
	threading.Thread(target=publish_humidity, args=(client, topic_humidity)).start()

	client.loop_stop()
