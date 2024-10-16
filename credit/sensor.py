import random
import time
def temperature():
	time.sleep(1)
	temp = random.randint(-10, 100)
	msg = f"temperature: {temp} Celsius"
	return msg

def humidity():
	time.sleep(1.5)
	humid = random.randint(0,100)
	msg = f"humidity: {humid}%"
	return msg
