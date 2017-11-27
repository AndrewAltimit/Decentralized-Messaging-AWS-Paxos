import socket
import _thread
import os, sys
import pickle
from event_module import *

ARRAY_INIT_SIZE = 8

# Proposer Class
class Proposer():
	def __init__(self, ID, server_config, log):
		self.ID = ID
		self.leader_list = [None] * ARRAY_INIT_SIZE
		self.server_config = server_config
		self.IP = server_config[ID]["IP"]
		self.port = server_config[ID]["PROPOSER_PORT"]
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
				print("Server: {} Proposer received data!".format(self.ID))
				
		except:
			# Restart listening thread
			_thread.start_new_thread(self.listen, ())
		
	def propose(self, slot, n):
		pass
		
	def accept(self, slot, n, event):
		pass
		
	def commit(self, slot, event):
		pass
		
	def fill_holes(self):
		pass
		
	def update_log(self):
		pass
	
	def isLeader(self, slot):
		return (getLeader(slot) == self.ID)
		
	def getLeader(self, slot):
		return self.leader_list[slot]
		
	def setLeader(self, slot, ID):
		while len(self.leader_list) - 1 < slot:
			self.extend_leader_list()
		self.leader_list[slot] = ID
		
	def extend_leader_list(self):
		size = len(self.leader_list)
		self.leader_list.extend([None] * size)
		
		
	# Given a destination IP and port, send a message
	def send_msg(self, dest_ip, dest_port, message):
		try:
			print("Server: {} Proposer sending message to IP {} port {}".format(self.ID, dest_ip, dest_port))
			self.sock.sendto(message, (dest_ip, dest_port))
		except:
			pass
			
	def send_all_acceptors(self, message):
		for ID in self.server_config:
			dest_ip = self.server_config[ID]["IP"]
			dest_port = self.server_config[ID]["ACCEPTOR_PORT"]
			self.send_msg(dest_ip, dest_port, message)
			
	def send_all_learners(self, message):
		for ID in self.server_config:
			dest_ip = self.server_config[ID]["IP"]
			dest_port = self.server_config[ID]["LEARNER_PORT"]
			self.send_msg(dest_ip, dest_port, message)