import random
import json

from paho.mqtt import client as mqtt_client

broker = 'rule28.i4t.swin.edu.au'
port = 1883
# Generate a client id with prefix and random number
client_id = f"python-mqtt-{random.randint(0, 1000)}"
username = "<103825154>"
password = "<103825154>"

def on_connect(client, userdata, flags, rc):
	if rc == 0:
		print("Connected to mqtt broker")
	else:
		print("failed to connect, return code %d\n", rc)

def connect_mqtt():
	client = mqtt_client.Client(client_id)
	client.username_pw_set(username, password)
	client.on_connect = on_connect
	client.connect(broker, port)
	return client

def on_message(client, userdata, msg):
	print("\n====================[SUB]====================")
	print(json.dumps({"topic": msg.topic, "qos": msg.qos, "retained": msg.retain, "message": msg.payload.decode()}, indent=4))
	print("=============================================")

if __name__ == "__main__":
	client = connect_mqtt()
	client.subscribe("public/#")
	client.on_message = on_message

	try:
		client.loop_forever()
	except KeyboardInterrupt:
		print("Terminate program")
