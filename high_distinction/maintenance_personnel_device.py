import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import paho.mqtt.client as mqtt
import json
import datetime
import uuid

import config

class MaintenancePersonnelDevice:
    def __init__(self, master):
        self.master = master
        self.master.title("Maintenance Personnel Device")
        self.master.geometry("800x600")

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.equipment_types = ["cnc_mill", "robot_arm", "agv", "injection_molder", "conveyor"]
        self.sensor_types = ["vibration", "temperature", "current", "position", "torque", "battery", "speed", "location", "pressure", "cycle_time", "load"]

        self.create_widgets()
        self.connect_mqtt()

    def create_widgets(self):
        # Equipment selection
        tk.Label(self.master, text="Select Equipment:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.equipment_var = tk.StringVar()
        self.equipment_dropdown = ttk.Combobox(self.master, textvariable=self.equipment_var, values=self.equipment_types)
        self.equipment_dropdown.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        self.equipment_dropdown.bind("<<ComboboxSelected>>", self.update_sensor_display)

        # Sensor data display
        self.sensor_frame = tk.Frame(self.master)
        self.sensor_frame.grid(row=1, column=0, columnspan=2, sticky="nswe", padx=5, pady=5)
        self.sensor_labels = {}

        for i, sensor in enumerate(self.sensor_types):
            tk.Label(self.sensor_frame, text=f"{sensor.capitalize()}:").grid(row=i, column=0, sticky="w")
            self.sensor_labels[sensor] = tk.Label(self.sensor_frame, text="N/A")
            self.sensor_labels[sensor].grid(row=i, column=1, sticky="w")

        # Alert display
        tk.Label(self.master, text="Alerts:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.alert_text = scrolledtext.ScrolledText(self.master, height=10)
        self.alert_text.grid(row=3, column=0, columnspan=2, sticky="nswe", padx=5, pady=5)

        # Configure grid
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(3, weight=1)

    def connect_mqtt(self):
        self.client.username_pw_set(config.USERNAME, config.PASSWORD)
        try:
            self.client.connect(config.BROKER, config.PORT)
            self.client.loop_start()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker")
            # Subscribe to all equipment and alert topics
            self.client.subscribe(f"{config.TOP_LEVEL_TOPIC}/factory/equipment/#")
            self.client.subscribe(f"{config.TOP_LEVEL_TOPIC}/factory/alerts/#")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            topic_parts = msg.topic.split('/')

            if topic_parts[-3] == "equipment":
                self.update_sensor_data(topic_parts[-2], topic_parts[-1], payload)
            elif topic_parts[-3] == "alerts":
                self.handle_alert(topic_parts[-2], payload)
        except json.JSONDecodeError:
            print(f"Received invalid JSON on topic {msg.topic}")

    def update_sensor_data(self, equipment_type, sensor_type, payload):
        if equipment_type == self.equipment_var.get():
            value = payload['value']
            unit = payload['unit']
            self.sensor_labels[sensor_type].config(text=f"{value} {unit}")

    def handle_alert(self, equipment_type, payload):
        timestamp = datetime.datetime.fromtimestamp(payload['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        alert_message = f"Alert for {equipment_type}:\n{payload['message']}\nLevel: {payload['alert_level']}"

        self.alert_text.insert(tk.END, f"[{timestamp}] {alert_message}\n")
        self.alert_text.see(tk.END)

        # Show message box for all alerts
        response = messagebox.askyesno("Alert", f"{alert_message}\n\nDo you want to send a maintenance request?")

        if response:
            self.send_maintenance_request(equipment_type, payload['message'])

    def send_maintenance_request(self, equipment_type, alert_data):
        request_id = str(uuid.uuid4())
        maintenance_request = {
            "request_id": request_id,
            "timestamp": int(datetime.datetime.now().timestamp()),
            "equipment_type": equipment_type,
            "alert_data": alert_data,
            "status": "pending"
        }

        topic = f"{config.TOP_LEVEL_TOPIC}/factory/maintenance/requests/{equipment_type}"
        self.client.publish(topic, json.dumps(maintenance_request))

        messagebox.showinfo("Maintenance Request", f"Maintenance request sent for {equipment_type} \nRequest ID: {request_id}")

    def update_sensor_display(self, event):
        selected_equipment = self.equipment_var.get()
        for sensor in self.sensor_types:
            self.sensor_labels[sensor].config(text="N/A")
        print(f"Selected equipment: {selected_equipment}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MaintenancePersonnelDevice(root)
    root.mainloop()
