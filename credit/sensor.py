import random
import time

def accelerometer():
	return {
		"x": round(random.uniform(-10, 10), 2),
		"y": round(random.uniform(-10, 10), 2),
		"z": round(random.uniform(-10, 10), 2),
		"unit": "m/s^2"
	}

def temperature():
	return {
		"temperature": round(random.uniform(20, 30), 2),
		"unit": "°C"
	}

def pressure():
	return {
		"pressure": round(random.uniform(980, 1050), 2),
		"unit": "kPa"
	}

def strain():
	return {
		"strain": round(random.uniform(0, 1000), 2),
		"unit": "μɛ"
	}

def rotary_encoder():
	return {
		"angle": round(random.uniform(0, 360), 1),
		"unit": "degrees"
	}
