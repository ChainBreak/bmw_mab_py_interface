#!/usr/bin/env python


import socket
import struct
import time
import threading
import weakref

class BmwMabInterface():
	
	def __init__(self,mab_ip):
		print(mab_ip)
		self.mab_ip = mab_ip
		self.receive_from_port = 5000
		self.send_to_port = 5001

		self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		self.recv_socket.bind(("0.0.0.0", self.receive_from_port))
		self.recv_socket.settimeout(1.0)
		
		self.recv_thread = threading.Thread(target=self.receiveLoop)

	def __enter__(self):	
		self.running = True
		self.recv_thread.start()


	def receiveLoop(self):
		while self.running:
			try:
				data, addr = self.recv_socket.recvfrom(1024) # buffer size is 1024 bytes
				bytes = bytearray(data)
			
				data_format = "Ifffdd"
				data_length = struct.calcsize(data_format)
			
				dataStruct = struct.unpack(data_format,data[:data_length])
				
			
				time.sleep(0.005)
			except socket.timeout:
				pass
			


	def getCarState(self):
		pass

	def setCarAction(self):
		pass

	def __exit__(self,*args):
		print("exit")
		self.running = False
		print("wait for join")
		self.recv_thread.join()
		print("Joined now done")

	
		
