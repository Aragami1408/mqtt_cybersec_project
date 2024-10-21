import paho.mqtt.client as mqtt
import time
import random
import json
import argparse
import os

import config

def generate_sensor_data(sensor_type):
	if sensor_type == "vibration":
		return round(random.uniform(0, 10), 2)  # mm/s^2
	elif sensor_type == "temperature":
		return round(random.uniform(20, 200), 1)  # °C
	elif sensor_type == "current":
		return round(random.uniform(0, 50), 1)  # Amperes
	elif sensor_type == "position":
		return [round(random.uniform(-180, 180), 1) for _ in range(3)]  # degrees for 3 joints
	elif sensor_type == "torque":
		return round(random.uniform(0, 100), 1)  # Nm
	elif sensor_type == "battery":
		return round(random.uniform(0, 100), 1)  # percentage
	elif sensor_type == "speed":
		return round(random.uniform(0, 5), 1)  # m/s
	elif sensor_type == "location":
		return [round(random.uniform(0, 100), 1) for _ in range(2)]  # x, y coordinates
	elif sensor_type == "pressure":
		return round(random.uniform(0, 200), 1)  # Bar
	elif sensor_type == "cycle_time":
		return round(random.uniform(10, 60), 1)  # seconds
	elif sensor_type == "load":
		return round(random.uniform(0, 1000), 1)  # kg
	else:
		return 0

def get_unit(sensor_type):
	units = {
		"vibration": "mm/s^2",
		"temperature": "Celsius",
		"current": "A",
		"position": "degrees",
		"torque": "Nm",
		"battery": "%",
		"speed": "m/s",
		"location": "m",
		"pressure": "Bar",
		"cycle_time": "s",
		"load": "kg"
	}
	return units.get(sensor_type, "")

class Equipment:
	def __init__(self, equipment_type):
		self.client = mqtt.Client(f"Equipment_{equipment_type}")
		self.client.username_pw_set(config.USERNAME, config.PASSWORD)
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		self.client.connect(config.BROKER, config.PORT)

		self.equipment_type = equipment_type

		self.sensor_configs = {
			"cnc_mill": ["vibration", "temperature", "current"],
			"robot_arm": ["position", "temperature", "torque"],
			"agv": ["battery", "speed", "location"],
			"injection_molder": ["pressure", "temperature", "cycle_time"],
			"conveyor": ["speed", "load", "temperature"]
		}

		self.maintenance_dir = "maintenance_log"
		if not os.path.exists(self.maintenance_dir):
			os.makedirs(self.maintenance_dir)

		self.sensor_types = self.sensor_configs.get(equipment_type, [])

	def on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			print(f"Connected to MQTT Broker: {self.equipment_type}")
			self.client.subscribe(f"{config.TOP_LEVEL_TOPIC}/factory/alerts/{self.equipment_type}/#")
			self.client.subscribe(f"public/#")
		else:
			print(f"Failed to connect, return code {rc}")

	def on_message(self, client, userdata, msg):
		try:
			if (msg.topic.startswith(f"{config.TOP_LEVEL_TOPIC}/factory/alerts")):
				payload = json.loads(msg.payload.decode())
				topic_parts = msg.topic.split("/")
				sensor_type = topic_parts[-1]

				self.generate_maintenance_message(sensor_type, payload)
		except json.JSONDecodeError:
			print(f"Received invalid JSON on topic {msg.topic}")
		except IndexError:
			print(f"Received message with invalid topic structure: {msg.topic}")

	def generate_maintenance_message(self, sensor_type, alert_data):
		maintenance_message = {
			"equipment_type": self.equipment_type,
			"sensor_type": sensor_type,
			"alert_level": alert_data['alert_level'],
			"message": alert_data['message'],
			"sensor_reading": alert_data['sensor_reading'],
			"threshold": alert_data['threshold'],
			"timestamp": alert_data['timestamp'],
			"maintenance_action": f"Check {sensor_type} on {self.equipment_type}"
		}

		topic = f"{config.TOP_LEVEL_TOPIC}/factory/maintenance/requests/{self.equipment_type}"
		payload = json.dumps(maintenance_message)
		self.client.publish(topic, payload)
		self.dump_maintenance_log(sensor_type, alert_data)

	def dump_maintenance_log(self, sensor_type, alert_data):
		maintenance_message = (
			"\n----------\n"
			f"Maintenance required for {self.equipment_type}\n"
			f"Sensor: {sensor_type}\n"
			f"Alert Level: {alert_data['alert_level']}\n"
			f"Message: {alert_data['message']}\n"
			f"Sensor Reading: {alert_data['sensor_reading']}\n"
			f"Threshold: {alert_data['threshold']}\n"
			f"Timestamp: {time.ctime(alert_data['timestamp'])}\n"
			"\n----------\n"
		)

		filename = os.path.join(self.maintenance_dir, f"{self.equipment_type}_maintenance.log")
		with open(filename, "a") as f:
			f.write(maintenance_message)

		print(f"Maintenance message logged for {self.equipment_type}")

	def publish_sensor_data(self):
		for sensor_type in self.sensor_types:
			topic = f"{config.TOP_LEVEL_TOPIC}/factory/equipment/{self.equipment_type}/{sensor_type}"
			payload = json.dumps({
				"timestamp": time.ctime(),
				"value": generate_sensor_data(sensor_type),
				"unit": get_unit(sensor_type)
			})
			self.client.publish(topic, payload)
			#print(f"Published to {topic}: {payload}")

	def run(self):
		self.client.loop_start()
		try:
			while True:
				self.publish_sensor_data()
				time.sleep(5)
		except KeyboardInterrupt:
			print(f"Sensor node stopped: {self.equipment_type}")
			self.client.loop_stop()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Equipment")
	parser.add_argument("equipment_type", choices=["cnc_mill", "robot_arm", "agv", "injection_molder", "conveyor"],
			help="Type of equipment to simulate")
	args = parser.parse_args()

	Equipment(args.equipment_type).run()
