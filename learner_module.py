import socket
import _thread
import os, sys
import pickle
from event_module import *


# Proposer Class
class Learner():
	def __init__(self, ID, server_config, log):
		self.ID = ID
		self.server_config = server_config
		self.IP = server_config[ID]["IP"]
		self.port = server_config[ID]["LEARNER_PORT"]
		self.log = log
		_thread.start_new_thread(self.listen, ())

		
	# Listen for incoming connections by binding to the socket specified in the hosts file
	def listen(self):
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			self.sock.bind((self.IP, self.port))
			while True:
				data, server = self.sock.recvfrom(4096)
				# do something with received data (best not to create new thread for this)
				print("Server: {} Learner received data!".format(self.ID))
				
		except:
			# Restart listening thread
			_thread.start_new_thread(self.listen, ())
			
			
			
	# Given a destination IP and port, send a message
	def send_msg(self, dest_ip, dest_port, message):
		try:
			print("Server: {} Learner sending message...".format(self.ID))
			self.sock.sendto(message, (dest_ip, dest_port))
		except:
			pass