import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import json
import paho.mqtt.client as mqtt
import config

class FactoryMonitorGUI:
	def __init__(self, master):
		self.master = master
		master.title("Factory Monitor")
		master.geometry("800x600")
		self.master.resizable(False, False)

		self.equipment_processes = {}
		self.equipment_types = ["cnc_mill", "robot_arm", "agv", "injection_molder", "conveyor"]
		self.sensor_types = [
			"vibration", "temperature", "current", "position", "torque", "battery", "speed", "location", "pressure", "cycle_time", "load"
		]

		self.client = None
		self.connect()

		self.create_widgets()

	def create_widgets(self):
		# Equipment Control Frame
		control_frame = ttk.LabelFrame(self.master, text="Equipment Control")
		control_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

		self.equipment_var = tk.StringVar()
		self.equipment_combo = ttk.Combobox(control_frame, textvariable=self.equipment_var)
		self.equipment_combo["values"] = (
			"cnc_mill", "robot_arm", "agv", "injection_molder", "conveyor"
		)
		self.equipment_combo.set("cnc_mill")
		self.equipment_combo.grid(row=0, column=1, padx=5, pady=5)

		self.start_button = ttk.Button(control_frame, text="Start", command=self.start_equipment)
		self.start_button.grid(row=0, column=2, padx=5, pady=5)

		self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_equipment)
		self.stop_button.grid(row=0, column=3, padx=5, pady=5)

		# Sensor Reading Frame
		readings_frame = ttk.LabelFrame(self.master, text="Sensor Readings")
		readings_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

		self.sensor_labels = {}
		for i, sensor in enumerate(self.sensor_types):
			tk.Label(readings_frame, text=f"{sensor.capitalize()}:").grid(row=i, column=0, sticky="w")
			self.sensor_labels[sensor] = tk.Label(readings_frame, text="N/A")
			self.sensor_labels[sensor].grid(row=i, column=1, sticky="w")

	def connect(self):
		self.client = mqtt.Client()
		self.client.username_pw_set(config.USERNAME, config.PASSWORD)
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		self.client.connect(config.BROKER, config.PORT)
		self.client.loop_start()

	def on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			messagebox.showinfo("MQTT", "Connected to MQTT Broker\n")
			self.client.subscribe(f"{config.TOP_LEVEL_TOPIC}/factory/equipment/#")
			self.client.subscribe(f"{config.TOP_LEVEL_TOPIC}/factory/alerts/#")
		else:
			messagebox.showerror("MQTT", f"Connection failed with code {rc}\n")

	def on_message(self, client, userdata, msg):
		try:
			payload = json.loads(msg.payload.decode())
			topic_parts = msg.topic.split("/")

			if "equipment" in topic_parts:
				self.update_sensor_reading(topic_parts[-2], topic_parts[-1], payload)
			elif "alerts" in topic_parts:
				self.show_alert(topic_parts[-2], topic_parts[-1], payload)
		except json.JSONDecodeError:
			messagebox.showerror("JSON Decode Error", f"Received invalid JSON on topic {msg.topic}")

	def update_sensor_reading(self, equipment_type, sensor_type, payload):
		if equipment_type == self.equipment_var.get():
			value = payload['value']
			unit = payload['unit']
			self.sensor_labels[sensor_type].config(text=f"{value} {unit}")

	def show_alert(self, equipment_type, sensor_type, payload):
		alert_message = f"Alert for {equipment_type} - {sensor_type}:\n{payload['message']}\nReading: {payload['sensor_reading']}\nThreshold: {payload['threshold']}"
		messagebox.showwarning("Equipment Alert", alert_message)

	def start_equipment(self):
		equipment = self.equipment_var.get()
		if equipment in self.equipment_processes:
			messagebox.showinfo("Info", f"{equipment} is already running")
			return

		try:
			process = subprocess.Popen(["python3", "equipment.py", equipment])
			self.equipment_processes[equipment] = process
			messagebox.showinfo("Info", f"Started {equipment} sensor readings")
		except Exception as e:
			messagebox.showerror("Error", f"Failed to start {equipment}: {str(e)}")

	def stop_equipment(self):
		equipment = self.equipment_var.get()
		if equipment not in self.equipment_processes:
			messagebox.showerror("Error", f"{equipment} is not running")
			return

		try:
			self.equipment_processes[equipment]
			self.equipment_processes[equipment].terminate()
			del self.equipment_processes[equipment]
			messagebox.showinfo("Info", f"{equipment} sensor terminated")
		except Exception as e:
			messagebox.showerror("Error", f"Failed to stop {equipment}: {str(e)}")


if __name__ == "__main__":
	process = subprocess.Popen(["python3", "monitor.py"])
	root = tk.Tk()
	app = FactoryMonitorGUI(root)
	def on_closing():
		app.stop_equipment()
		if messagebox.askokcancel("Quit", "Do you want to quit?"):
			root.destroy()
	root.protocol("WM_DELETE_WINDOW", on_closing)
	root.mainloop()
	process.terminate()
