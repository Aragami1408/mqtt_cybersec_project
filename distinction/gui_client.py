import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import paho.mqtt.client as mqtt

class MQTTClient:
	def __init__(self, master):
		self.master = master
		self.master.title("MQTT Client")
		self.master.geometry("500x600")
		self.master.resizable(False, False)

		self.client = mqtt.Client()
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message

		self.create_widgets()

	def create_widgets(self):
		# Connection Frame
		connection_frame = ttk.LabelFrame(self.master, text="Broker Connection")
		connection_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

		ttk.Label(connection_frame, text="Broker:").grid(row=0, column=0, sticky="w")
		self.broker_entry = ttk.Entry(connection_frame)
		self.broker_entry.grid(row=0, column=1)
		self.broker_entry.insert(0, "rule28.i4t.swin.edu.au")

		ttk.Label(connection_frame, text="Port:").grid(row=1, column=0, sticky="w")
		self.port_entry = ttk.Entry(connection_frame)
		self.port_entry.grid(row=1, column=1)
		self.port_entry.insert(0, "1883")

		ttk.Label(connection_frame, text="Username:").grid(row=2, column=0, sticky="w")
		self.username_entry = ttk.Entry(connection_frame)
		self.username_entry.grid(row=2, column=1)

		ttk.Label(connection_frame, text="Password:").grid(row=3, column=0, sticky="w")
		self.password_entry = ttk.Entry(connection_frame, show="*")
		self.password_entry.grid(row=3, column=1)

		self.connect_button = ttk.Button(connection_frame, text="Connect", command=self.connect)
		self.connect_button.grid(row=4, column=0, columnspan=2, pady=5)

		# Subscribe Frame
		subscribe_frame = ttk.LabelFrame(self.master, text="Subscribe")
		subscribe_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

		ttk.Label(subscribe_frame, text="Topic:").grid(row=0, column=0, sticky="w")
		self.subscribe_entry = ttk.Entry(subscribe_frame)
		self.subscribe_entry.grid(row=0, column=1)

		ttk.Label(subscribe_frame, text="QoS:").grid(row=0, column=2, padx=5)
		self.qos_subscribe = tk.StringVar()
		self.qos_subscribe_combobox = ttk.Combobox(subscribe_frame, textvariable=self.qos_subscribe)
		self.qos_subscribe_combobox.grid(row=0, column=3)
		self.qos_subscribe_combobox['values'] = (
			'0',
			'1',
			'2'
		)
		self.qos_subscribe_combobox.current(0)

		self.subscribe_button = ttk.Button(subscribe_frame, text="Subscribe", command=self.subscribe)
		self.subscribe_button.grid(row=1, column=0, columnspan=2, pady=5)

		# Publish Frame
		publish_frame = ttk.LabelFrame(self.master, text="Publish")
		publish_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

		ttk.Label(publish_frame, text="Topic:").grid(row=0, column=0, sticky="w")
		self.publish_topic_entry = ttk.Entry(publish_frame)
		self.publish_topic_entry.grid(row=0, column=3)

		ttk.Label(publish_frame, text="Message:").grid(row=1, column=0, sticky="w")
		self.publish_message_entry = ttk.Entry(publish_frame)
		self.publish_message_entry.grid(row=1, column=3)

		ttk.Label(publish_frame, text="Retain:").grid(row=2,column=0, sticky="w", columnspan=2)
		self.retain = tk.IntVar()
		self.retain_checkbutton = ttk.Checkbutton(publish_frame, variable=self.retain, onvalue=1, offvalue=0)
		self.retain_checkbutton.grid(row=2, column=1)

		ttk.Label(publish_frame, text="QoS:").grid(row=2, column=2, padx=5)
		self.qos_publish = tk.StringVar()
		self.qos_publish_combobox = ttk.Combobox(publish_frame, textvariable=self.qos_publish)
		self.qos_publish_combobox.grid(row=2,column=3)
		self.qos_publish_combobox['values'] = (
			'0',
			'1',
			'2'
		)
		self.qos_publish_combobox.current(0)

		self.publish_button = ttk.Button(publish_frame, text="Publish", command=self.publish)
		self.publish_button.grid(row=3, column=0, columnspan=2, pady=5)

		# Messages Frame
		messages_frame = ttk.LabelFrame(self.master, text="Messages")
		messages_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

		self.messages_text = scrolledtext.ScrolledText(messages_frame, height=15)
		self.messages_text.pack(expand=True, fill="both")

		self.master.grid_columnconfigure(0, weight=1)
		self.master.grid_rowconfigure(3, weight=1)

	def connect(self):
		broker = self.broker_entry.get()
		port = int(self.port_entry.get())
		username = self.username_entry.get()
		password = self.password_entry.get()

		if username and password:
			self.client.username_pw_set(username, password)

			try:
				self.client.connect(broker, port)
				self.client.loop_start()
			except Exception as e:
				messagebox.showerror("Connection Error", str(e))

	def subscribe(self):
		topic = self.subscribe_entry.get()
		self.client.subscribe(topic, qos=int(self.qos_subscribe.get()))
		self.messages_text.insert(tk.END, f"Subscribed to {topic}\n")

	def publish(self):
		topic = self.publish_topic_entry.get()
		message = self.publish_message_entry.get()
		self.client.publish(topic, message, qos=int(self.qos_publish.get()), retain=bool(self.retain.get()))
		self.messages_text.insert(tk.END, f"Published to {topic}: {message}\n")
		self.messages_text.insert(tk.END, f"\tQoS: {int(self.qos_publish.get())}. Retain = {bool(self.retain.get())}\n")

	def on_connect(self, client, userdata, flags, rc):
		broker = self.broker_entry.get()
		port = int(self.port_entry.get())
		if rc == 0:
			messagebox.showinfo("Connection", f"Connected to {broker}:{port}")
			self.messages_text.insert(tk.END, "Connected to MQTT Broker\n")
		else:
			self.messages_text.insert(tk.END, f"Connection failed with code {rc}\n")

	def on_message(self, client, userdata, msg):
		self.messages_text.insert(tk.END, f"Received message on {msg.topic}: {msg.payload.decode()}\n")
		self.messages_text.insert(tk.END, f"\tQos: {int(self.qos_subscribe.get())}\n")

if __name__ == "__main__":
	root = tk.Tk()
	app = MQTTClient(root)
	root.mainloop()
