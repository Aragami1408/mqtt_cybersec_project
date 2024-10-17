import random
import time
def temperature():
	return {
		"sensor_type": "temperature",
		"value": round(random.uniform(20, 30), 2),
		"unit": "Celsius"
	}

def humidity():
	return {
		"sensor_type": "humidity",
		"value": round(random.uniform(30, 80), 2),
		"unit": "%"
	}

def pressure():
	return {
		"sensor_type": "pressure",
		"value": round(random.uniform(980, 1050), 2),
		"unit": "hPa"
	}

def light():
	return {
		"sensor_type": "light",
		"value": round(random.uniform(0, 1000), 2),
		"unit": "Lux"
	}
