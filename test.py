#!/usr/bin/env python

from BmwMabInterface import bmwMabInterface
import time
import math


with bmwMabInterface.BmwMabInterface("192.168.0.5") as mab:
	print mab
	try:
		while True:
			time.sleep(0.1)
			data = mab.getCarData()
			print("\n\n")
			for item in data.items():
				print("%30s: %s" % item)
				
			for theta in range(0,360,2):
				s = math.sin(theta/180.0*3.14159)
				steerAngle = s * 25.0
				mab.setCarData({"ref_steering_angle": steerAngle})
				time.sleep(0.05)
				
#			print("\n\n")	
#			for fmt,default,name,desc in mab.sendDataDescription():
#				print(name)
#				for angle in range(0,360,5):
#					s = 10*math.sin(angle/180.0*3.14159)
#					mab.setCarData({name: s})
#					time.sleep(0.02)
#				mab.setCarData({name: 0.0})
				
	except KeyboardInterrupt:
		pass
print("\n\ndone")

	
