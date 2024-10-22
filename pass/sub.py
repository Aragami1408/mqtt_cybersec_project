import random

from paho.mqtt import client as mqtt_client

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
		print("Connected to mqtt broker")
	else:
		# if the client failed to connect to the broker
		print("failed to connect, return code %d\n", rc)

# use this function to initiate connection
# before connect to the mqtt broker, provide username, password, broker and port to the client instance
def connect_mqtt():
	client = mqtt_client.Client(client_id)
	client.username_pw_set(username, password)
	client.on_connect = on_connect
	client.connect(broker, port)
	return client

# When the client receives message from subscribed topics
# in this case, it prints out received message and which topic it received from
def on_message(client, userdata, msg):
	print(f"received `{msg.payload.decode()}` from `{msg.topic}` topic")

# use subscribe function to subscribe to a topic
def subscribe(client, topic):
	client.subscribe(topic)
	client.on_message = on_message

if __name__ == "__main__":
	client = connect_mqtt()
	subscribe(client, "<103825154>/temperature")
	try:
		client.loop_forever()
	except KeyboardInterrupt:
		print("Terminate program")
