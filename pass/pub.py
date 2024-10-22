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

# When the client initiate connection
def on_connect(client, userdata, flags, rc):
	if rc == 0:
		# if the client successfully connected to the broker
		print("Connected to MQTT Broker")
	else:
		# if the client failed to connect to the broker
		print("Failed to connect, return code %d\n", rc)

# use this function to initiate connection
# before connect to the mqtt broker, provide username, password, broker and port to the client instance
def connect_mqtt():
	client = mqtt_client.Client(client_id)
	client.username_pw_set(username, password)
	client.on_connect = on_connect
	client.connect(broker, port)
	return client

# one private topic
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
