#!/usr/bin/python
import os
import subprocess
from random import randint
from time import sleep
from threading import Thread
from datetime import datetime



class BTDetector(Thread):

	stopped = None
	hub = None
	paired_devices = None
	paired_status = None #For every time the device is seen its get incremented one, else subtracted
	paired_status_maximum = 3
	
	def __init__(self, hub):
		Thread.__init__(self)
		
		#Sudo required
		if os.geteuid() != 0:
			raise Exception("You need to have root privileges. Exiting.")
			
		self.stopped = False
		self.hub = hub
		self.paired_devices = []
		
		p = subprocess.Popen('hciconfig -a', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		lines = p.stdout.readlines()
		if not (len(lines) > 0 and "hci0" in lines[0]):
			raise Exception("No BT device Connected")
		
		#Configures the Interface
		subprocess.Popen('sudo hciconfig hci0 reset', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		subprocess.Popen('sudo hciconfig hci0 noscan', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		subprocess.Popen('sudo hciconfig hci0 name BT_$(hostname)', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		subprocess.Popen('sudo hciconfig hci0 afhmode 1', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		subprocess.Popen('sudo hciconfig hci0 sspmode 0', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		subprocess.Popen('sudo hciconfig hci0 lm MASTER', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		
		#Get Pared Devices
		self.renew_paired_list()

	def register_phone(self, mac, pin):
		
		mac = mac.upper()
		
		#removes first if already paired
		if mac in self.paired_devices:
			self.remove_phone(mac)
		
		p = subprocess.Popen('echo '+pin+' | sudo bluez-simple-agent hci0 '+mac, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		lines = p.stdout.readlines()
		subprocess.Popen('sudo bluez-test-device trusted '+mac+' yes', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		
		if lines == 3 and "New device" in lines[2]:
			self.renew_paired_list()
			return "Pair OK"
		else:
			return "Pair Fail"

	def remove_phone(self, mac):
		subprocess.Popen('sudo bluez-test-device remove '+mac, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

	def renew_paired_list(self):
		p = subprocess.Popen('sudo bluez-test-device list', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		lines = p.stdout.readlines()
		new_list = []
		for line in lines:
			found_mac = line.split()[0]
			new_list += [found_mac]
		self.paired_devices = new_list

	def get_paired(self):
		return self.paired_devices

	def stop(self):
		self.stopped = True
	
	#Checks if the device is on using l2ping
	def l2ping(self, mac):
		p = subprocess.Popen('sudo l2ping '+mac+' -s 0 -c 1', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
		lines = p.stdout.readlines()
		device_on = False
		if len(lines) == 3 and mac in lines[1] and '1 received' in lines[2]:
			device_on = True
		return device_on
		
	def run(self):
		count = 0
		while not self.stopped:
			for device in self.paired_devices:
				status = self.l2ping(device)
				#self.update_device_status(device, status)
				#todo uncoment
				count += 1
				#print count, device
			sleep(1)
			
	def device_status(self, device):
		print "Device Status not Implemented"
			 
	def update_device_status(self, device, status):

		if not self.paired_status:
			self.paired_status = []
				
		for x in self.paired_status:
			print x
			if device == x[0]:
				old_status = x[1]
				new_status = old_status + status
				if not new_status > self.paired_status_maximum and not new_status < 0:
					x[1] = new_status
					return
									
		#if not inicialized creates new variable
		print 'Not found in the list'
		if status > 0 #TODO HERE
		#TODO HERE
		if not len(self.paired_status) > 0:
			self.paired_status = [[device, status]]
		else:
			self.paired_status += [device, status]
		print self.paired_status			
			  
		
	def update(self):
		print "Update not Implemented"

#Runs only if called
if __name__ == "__main__":

	started = datetime.now()

	print "#TEST#"
	print "#Starting#"
	d = BTDetector(None)
	#print d.register_phone('40:B0:FA:3D:5F:08', '0000')
	print d.get_paired()
	#d.l2ping('40:B0:FA:3D:5F:08')
	d.start()
	print "#Sttoped#\n\n"
