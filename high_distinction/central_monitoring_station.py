import paho.mqtt.client as mqtt
import time
import random
import json
import argparse
import logging

import config

EQUIPMENT_THRESHOLDS = {
	"cnc_mill": {
		"vibration": 8.0,
		"temperature": 100.0,
		"current": 45.0
	},
	"robot_arm": {
		"position": None,
		"temperature": 150.0,
		"torque": 82.0
	},
	"agv": {
		"battery": 15,
		"speed": 4,
		"location": None,
	},
	"injection_molder": {
		"pressure": 180,
		"temperature": 175.0,
		"cycle_time": 45.0
	},
	"conveyor": {
		"speed": 4,
		"load": 925.0,
		"temperature": 184.0
	},
}

class CentralMonitorStation:
	def __init__(self):
		self.client = mqtt.Client("CentralMonitoring")
		self.client.username_pw_set(config.USERNAME, config.PASSWORD)
		self.client.on_connect = self.on_connect
		self.client.on_message = self.on_message
		self.client.connect(config.BROKER, config.PORT)

		self.equipment_thresholds = EQUIPMENT_THRESHOLDS

	def on_connect(self, client, userdata, flags, rc):
		if rc == 0:
			print("Connected to MQTT Broker")
			self.client.subscribe(f"{config.TOP_LEVEL_TOPIC}/factory/equipment/#")
		else:
			print(f"Failed to connect, return code {rc}")

	def on_message(self, client, userdata, msg):
		try:
			payload = json.loads(msg.payload.decode())
			topic_parts = msg.topic.split("/")
			equipment_type = topic_parts[len(topic_parts)-2]
			sensor_type = topic_parts[len(topic_parts)-1]

			print(f"Received: {equipment_type} {sensor_type}: {payload['value']} {payload['unit']}")
			self.process_sensor_data(equipment_type, sensor_type, payload['value'])
		except json.JSONDecodeError:
			print(f"Received invalid JSON on topic {msg.topic}")
		except IndexError:
			print(f"Received message with invalid topic structure: {msg.topic}")

	def process_sensor_data(self, equipment_type, sensor_type, value):
		threshold = self.equipment_thresholds[equipment_type][sensor_type]
		if threshold is not None:
			if value > threshold:
				self.generate_alert(equipment_type, sensor_type, value, threshold)

	def generate_alert(self, equipment_type, sensor_type, value, threshold):
		topic = f"{config.TOP_LEVEL_TOPIC}/factory/alerts/{equipment_type}/{sensor_type}"
		payload = json.dumps({
			"timestamp": int(time.time()),
			"alert_level": "warning",
			"message": f"{sensor_type.capitalize()} high threshold",
			"sensor_reading": value,
			"threshold": threshold
		})
		self.client.publish(topic, payload)
		print(f"Alert generated: {topic} - {payload}")

	def run(self):
		print("Central Monitor Station started")
		self.client.loop_forever()

if __name__ == "__main__":

	CentralMonitorStation().run()
