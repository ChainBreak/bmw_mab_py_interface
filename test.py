#!/usr/bin/env python

from BmwMabInterface import bmwMabInterface
import time
import math


with bmwMabInterface.BmwMabInterface() as mab:

	print mab
	try:
		variables = ["sys_heartbeat_counter"]
		while True:
			print("\n\n")
			for var in variables:
				print("%30s: %s" % (var,mab.getCarData(var)))
				
			for theta in range(0,360,10):
				s = math.sin(theta/180.0*3.14159)
				steerAngle = s * 25.0
				mab.setCarData("ref_steering_angle", steerAngle)
				time.sleep(0.05)

				
	except KeyboardInterrupt:
		pass
print("\n\ndone")

	
