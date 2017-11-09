#!/usr/bin/env python

from BmwMabInterface import bmwMabInterface
import time
import math


with bmwMabInterface.BmwMabInterface() as bmw:

	print bmw
	try:
		variables = ["sys_heartbeat_counter"]
		while True:
			print("\n\n")
			for fmt,name,desc in bmw.getRecvDataDescription():
				print("%34s: %s" % (name,bmw.getCarData(name)))
			time.sleep(0.3)
#			for theta in range(0,360,10):
#				s = math.sin(theta/180.0*3.14159)
#				steerAngle = s * 25.0
#				bmw.setCarData("ref_steering_angle", steerAngle)
#				time.sleep(0.05)

				
	except KeyboardInterrupt:
		pass
print("\n\ndone")

	
