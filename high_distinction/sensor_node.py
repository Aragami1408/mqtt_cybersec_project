import paho.mqtt.client as mqtt
import time
import random
import json
import argparse

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

class SensorNode:
	def __init__(self, equipment_type):
		self.client = mqtt.Client(f"SensorNode_{equipment_type}")
		self.client.username_pw_set(config.USERNAME, config.PASSWORD)
		self.client.on_connect = self.on_connect
		self.client.connect(config.BROKER, config.PORT)

		self.equipment_type = equipment_type

		self.sensor_configs = {
			"cnc_mill": ["vibration", "temperature", "current"],
			"robot_arm": ["position", "temperature", "torque"],
			"agv": ["battery", "speed", "location"],
			"injection_molder": ["pressure", "temperature", "cycle_time"],
			"conveyor": ["speed", "load", "temperature"]
		}

		self.sensor_types = self.sensor_configs.get(equipment_type, [])

	def on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			print(f"Connected to MQTT Broker: {self.equipment_type}")
		else:
			print(f"Failed to connect, return code {rc}")

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
				time.sleep(1)  # Publish every 1 sec
		except KeyboardInterrupt:
			print(f"Sensor node stopped: {self.equipment_type}")
			self.client.loop_stop()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Sensor Node")
	parser.add_argument("equipment_type", choices=["cnc_mill", "robot_arm", "agv", "injection_molder", "conveyor"],
			help="Type of equipment to simulate")
	args = parser.parse_args()

	SensorNode(args.equipment_type).run()
