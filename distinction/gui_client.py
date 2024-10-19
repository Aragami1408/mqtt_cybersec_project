import tkinter as tk
from tkinter import scrolledtext, messagebox
import random
import json
import hashlib
from paho.mqtt import client as mqtt_client

broker = 'rule28.i4t.swin.edu.au'
#broker = "broker.emqx.io"
port = 1883
client_id = f"python-mqtt-{random.randint(0, 1000)}"
username = "<103825154>"
password = "<103825154>"

class MQTTClient:
	def __init__(self, master):
		self.master = master
		self.master.title("Simple MQTT Client")
		self.master.geometry("800x600")

		self.client = mqtt_client.Client(client_id)
		self.client.username_pw_set(username, password)
		self.client.on_connect = self.on_connect
		self.client.connect(broker, port)

		self.create_widgets()
		self.connect()

	def create_widgets(self):
		# Subscribe
		tk.Label(self.master, text="Subscribe Topic:").grid(row=0, column=0, sticky="w")
		self.subscribe_entry = tk.Entry(self.master)
		self.subscribe_entry.grid(row=0, column=1)

		self.subscribe_button = tk.Button(self.master, text="Subscribe", command=self.subscribe)
		self.subscribe_button.grid(row=1,column=1)

		# Publish
		tk.Label(self.master, text="Publish Topic:").grid(row=2,column=0, sticky="w")
		self.publish_topic_entry = tk.Entry(self.master)
		self.publish_topic_entry.grid(row=2, column=1)

		tk.Label(self.master, text="Message:").grid(row=3,column=0, sticky="w")
		self.publish_message_entry = tk.Entry(self.master)
		self.publish_message_entry.grid(row=3,column=1)

		self.publish_button = tk.Button(self.master, text="Publish", command=self.publish)
		self.publish_button.grid(row=4,column=1,columnspan=2)

		self.messages_text = scrolledtext.ScrolledText(self.master, height=15)
		self.messages_text.grid(row=5,column=0,columnspan=3,padx=5,pady=5)

	def on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			self.messages_text.insert(tk.END, "Connected to MQTT Broker\n")
		else:
			self.messages_text.insert(tk.END, f"Failed to connect, return code {rc}\n")

	def connect(self):
		try:
			self.client.loop_start()
		except Exception as e:
			messagebox.showerror("Connection Error", str(e))

	def subscribe(self):
		topic = self.subscribe_entry.get()
		self.client.subscribe(topic)
		self.client.on_message = self.on_message
		self.messages_text.insert(tk.END, f"Subscribed to {topic}\n")

	def publish(self):
		topic = self.publish_topic_entry.get()
		content = self.publish_message_entry.get()
		signature = hashlib.sha256(content.encode()).hexdigest()
		message = json.dumps({"topic": topic, "hash": signature, "message": content})
		result = self.client.publish(topic, message)
		if result[0] == 0:
			self.messages_text.insert(tk.END, "\n--------------------[PUB]--------------------\n")
			self.messages_text.insert(tk.END, message)
			self.messages_text.insert(tk.END,"\n")
			self.messages_text.insert(tk.END, "---------------------------------------------\n")
		else:
			self.messages_text.insert(tk.END, f"Failed to send message to topic {topic}")

	def on_message(self, client, userdata, msg):
		self.messages_text.insert(tk.END, "\n====================[SUB]====================\n")
		self.messages_text.insert(tk.END, json.dumps({"topic": msg.topic, "qos": msg.qos, "retained": msg.retain, "message": msg.payload.decode()}, indent=4))
		self.messages_text.insert(tk.END,"\n")
		self.messages_text.insert(tk.END, "=============================================\n")


if __name__ == "__main__":
	root = tk.Tk()
	app = MQTTClient(root)
	root.mainloop()
