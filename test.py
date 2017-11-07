#!/usr/bin/env python

from BmwMabInterface import bmwMabInterface
import time
with bmwMabInterface.BmwMabInterface("192.168.0.5") as mab:
	try:
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		pass
print("done")

	
