#!/usr/bin/env python


import socket
import struct
import time
import threading
import weakref

class BmwMabInterface():
	"""
	---BMW MicroAutoBox Interface---
	This is an ethernet interface to the MicroAutoBox which controls
	the self driving BMW. The interface has two asynchronous loops, one that
	continuously reads and one that continuously writes to the MicroAutoBox
	over the UDP enthernet connection. 
	
	The BmwMabInterface class must be instaciated inside a with context 
	manager.
	e.g.
	with BmwMabInterface() as bmw:
		bmw.setCarData("ref_steering_angle",25.0)
	
	Reading Data:
	The mehtod getRecvDataDescription() returns a list of all the variables
	that are received from the MicroAutoBox. All the variables that is read
	from the MicroAutoBox are stored in a dictionary that can be accessed 
	with getCarData(variable_name).
	e.g. speed = bmw.getCarData("car_velocity")
	
	Sending Data:
	The method getSendDataDescription() returns a list of all the variables
	that can be written to the MicroAutoBox. All the variables that are 
	written to the MicroAutoBox are stored in a dictionary that can be
	modified with setCarData(variable_name,value).
	e.g. bmw.setCarData("ref_steering_angle",25.0)
	Note that the variables "heartbeat_counter" and "sys_uptime" are modified
	internally.
	
	Your ip must be 192.168.0.10
	
	"""
	
	
	def __init__(self):
		"""
		Constructor
		"""
		
		#socket ips and ports
		self.mab_ip = "192.168.0.5"
		self.receive_from_port = 5000
		self.send_to_port = 5001
		
		#Create socket objects
		self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		
		#bind receive socket
		self.recv_socket.bind(("0.0.0.0", self.receive_from_port))
		self.recv_socket.settimeout(0.1)
		
		#set up send receive threads
		self.recv_thread = threading.Thread(target=self.__receiveLoop)
		self.recv_data_lock = threading.Lock()
		
		self.send_thread = threading.Thread(target=self.__sendLoop)
		self.send_data_lock = threading.Lock()
		
		#Setup dicts and lists for receive data
		self.recv_format = ""
		self.recv_data_dict = {}
		self.recv_data_name_list = []
		
		for fmt,name,desc in self.getRecvDataDescription():
			self.recv_format += fmt
			self.recv_data_dict[name] = 0.0
			self.recv_data_name_list.append(name)
		
		#Setup dicts and lists for send data
		self.send_format = ""
		self.send_data_dict = {}
		self.send_data_name_list = []
		
		for fmt,default,name,desc in self.getSendDataDescription():
			self.send_format += fmt
			self.send_data_dict[name] = default
			self.send_data_name_list.append(name)

	
	def __enter__(self):
		"""
		The enter method is called by the with context manager.
		It starts the receiving and sending threads
		"""	
		self.running = True
		self.recv_thread.start()
		self.send_thread.start()
		return self
		
	def __exit__(self,*args):
		"""
		The exit method is called by the with context manager.
		It stops the receiving and sending threads
		"""	
		self.running = False	
		self.recv_thread.join()
		self.send_thread.join()

	def __receiveLoop(self):
		"""The receive loop method is private and should only be called by
		the receive thread"""
		heartbeat_count = 0
		last_heartbeat_count = 0
		watchdog_time = time.time()
		while self.running:
			try:
				#read in data from socket
				data, addr = self.recv_socket.recvfrom(1024) # buffer size is 1024 bytes
				
				data_length = struct.calcsize(self.recv_format)
				dataStruct = struct.unpack(self.recv_format,data[:data_length])
				
				with self.recv_data_lock:
					for i in range(len(self.recv_data_name_list)):
						name = self.recv_data_name_list[i]
						self.recv_data_dict[name] = dataStruct[i]
					heartbeat_count = self.recv_data_dict["sys_heartbeat_counter"]
					
				time.sleep(0.005)
				
			except socket.timeout:
				pass
				
			if last_heartbeat_count != heartbeat_count:
				last_heartbeat_count = heartbeat_count
				watchdog_time = time.time()
				
			if time.time() - watchdog_time > 0.5:
				print("timeout")
				
				
				
	def __sendLoop(self):
		"""The send loop method is private and should only be called by
		the send thread"""
		counter = 0
		
		data = []
		for name in self.send_data_name_list:
			data.append(self.send_data_dict[name])
			
		while self.running:
			counter += 1
			try:
				with self.send_data_lock:
					self.send_data_dict["heartbeat_counter"] = counter
					i = 0
					for name in self.send_data_name_list:
						data[i] = self.send_data_dict[name]
						i+= 1
					
				bytes = struct.pack(self.send_format,*data)
				
				self.send_socket.sendto(bytes, (self.mab_ip, self.send_to_port))
				time.sleep(0.04)
				
			except socket.timeout:
				pass
			


	def getCarData(self, variable_name):
		"""
		Call this method to get the value for the variable name given.
		Call getRecvDataDescription() to get a list of available variables.
		"""
		with self.recv_data_lock:
			return self.recv_data_dict[variable_name]
		

	def setCarData(self,variable_name, value):
		"""
		Call this method to set the value for the variable name given.
		Call getSendDataDescription() to get a list of available variables.
		"""
		with self.send_data_lock:
				if variable_name in self.send_data_dict:
					self.send_data_dict[variable_name] = value
					print("%s: %s" % (variable_name, value))
			
		
	
	
	def getSendDataDescription(self):
		#(data format, variable name, description)
		return [
			("i",0,"heartbeat_counter","Counter 32-bit Increment by one"),
			("f",0,"sys_uptime","Time since start"),
			("f",0,"ref_steering_angle","Reference Steering Angle"),
			("f",0,"ref_velocity","Reference Velocity"),
			("f",0.2,"ref_acceleration",""),
			("f",0.2,"ref_deacceleration","")
		]
	
	def getRecvDataDescription(self):
		#(data format, variable name, description)
		return [
			("i","sys_heartbeat_counter","Counter 32-bit Increment by one"),
			("f","sys_uptime","Time since start"),
			("f","car_steering_angle","Steering Angle"),
			("f","car_velocity","Velocity"),
			("i","swift_status_bits","Swift Status 64-bit or 32 bit"),
			("f","swift_utc_of_position_fix","Swift UTC of position fix"),
			("d","swift_latitude","Swift Latitude"),
			("d","swift_longitude","Swift Longitude"),
			("f","swift_gps_quality_indicator","Swift GPS Quality Indicator"),
			("f","swift_no_of_satellites","Swift No of Satelites "),
			("f","swift_hdop","Swift HDOP"),
			("f","swift_orthometric_height","Swift Orthometric Height"),
			("f","swift_age_of_dgps_correction_data","Swift Age of DGPS correction Data"),
			("f","swift_ground_speed_in_km_h","Swift speed over ground in km/h"),
			("f","swift_orientation_to_north","Swift orientation to north"),
			("f","swift_gps_lat_error_in_m","Swift GPS Error in m"),
			("f","swift_gps_long_error_in_m","Swift GPS Error in m"),
			("f","swift_gps_height_error_in_m","Swift GPS Error in m"),
			("i","swift_reserverd_1","Swift reserverd"),
			("i","swift_reserverd_2","Swift reserverd"),
			("i","swift_reserverd_3","Swift reserverd"),
			("i","swift_reserverd_4","Swift reserverd"),
			("f","imu_accel_x","IMU a_x"),
			("f","imu_accel_y","IMU a_y"),
			("f","imu_accel_z","IMU a_z"),
			("f","imu_gyro_x","IMU gyro_x"),
			("f","imu_gyro_y","IMU gyro_y"),
			("f","imu_gyro_z","IMU gyro_z"),
			("f","imu_magnetic_x","magnetic Field x"),
			("f","imu_magnetic_y","magnetic Field y"),
			("f","imu_magnetic_z","magnetic Field z"),
			("f","imu_temperature","Temperature"),
			("f","imu_pressure","Pressure "),
			("f","imu_altitude","Altitude"),
			("f","imu_time_since_last_message","time since last sending IMU info"),
			("f","imu_reserved_1","IMU reserved"),
			("f","ekf_position_x","EKF - position x"),
			("f","ekf_position_y","EKF - position y"),
			("f","ekf_velocity_x","EKF - velocity x"),
			("f","ekf_velocity_y","EKF - velocity y"),
			("f","ekf_heading_to_east","EKF - heading to east"),
			("i","ekf_status","EKF - status"),
			("i","ekf_reserved","EKF - reserved"),
			("i","ekf_reserved","EKF - reserved"),
			("f","eps_steering_angle","EPS - steering angle"),
			("f","eps_motor_speed_velocity","EPS - motor speed velocity"),
			("f","eps_torque","EPS - Torque"),
			("f","eps_state","EPS - state"),
			("f","eps_steering_wheel_torque","EPS - steering wheel torque"),
			("f","eps_reserved_1","EPS - reserved"),
			("f","eps_reserved_2","EPS - reserved"),
			("f","eps_reserved_3","EPS - reserved"),
			("f","dsc_speed","DSC - speed"),
			("f","dsc_brake_press","DSC - brake press"),
			("f","dsc_brake_press_fl","DSC - brake press FL"),
			("f","dsc_brake_press_fr","DSC - brake press FR"),
			("f","dsc_brake_press_rl","DSC - brake press RL"),
			("f","dsc_brake_press_rr","DSC - brake press RR"),
			("f","dsc_wheel_speed_fl","DSC - wheel speed FL"),
			("f","dsc_wheel_speed_fr","DSC - wheel speed FR"),
			("f","dsc_wheel_speed_rl","DSC - wheel speed RL"),
			("f","dsc_wheel_speed_rr","DSC - wheel speed RR"),
			("f","dsc_steering_angle","DSC - steering angle"),
			("f","dsc_change_of_steering_angle","DSC - change of steering angle"),
			("f","dsc_time_since_last_message","DSC time since last message"),
			("f","dsc_reserved_1","DSC - reserved"),
			("f","dsc_reserved_2","DSC - reserved"),
			("f","dsc_reserved_3","DSC - reserved"),
			("i","hmi_status_bits","Status HMI"),
			("i","hmi_input_bits","Input HMI"),
			("i","hmi_reserved_1","HMI reserved"),
			("i","hmi_reserved_2","HMI reserved"),
			("f","car_footpedal_pos","Footpedal Pos"),
			("f","vel_controller_output","vel Controller Output"),
			("i","car_footpedal_status_bits","Footpedal Status"),
			("i","car_footpedal_reserved_1","Footpedal reserved"),
			("f","car_reference_velocity","reference velocity"),
			("f","car_reference_acceleration","reference acceleration"),
			("f","lc_deviation_to_ref_track","deviation to ref track"),
			("f","lc_deviation_at_lad","deviation at LAD"),
			("f","lc_p_gain","P Gain"),
			("f","lc_d_gain","D Gain"),
			("f","lc_lad_distance","LAD distance"),
			("f","lc_reference_track_pos","reference track pos"),
			("f","lc_reference_track_element","reference track element"),
			("f","lc_reserved_1","reserved"),
			("f","lc_reserved_2","reserved"),
			("f","lc_reserved_3","reserved")
		]


	
		
