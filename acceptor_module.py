import socket
import _thread
import os, sys
import pickle
from event_module import *

# Initial array sizes, double as needed for each reallocation
ARRAY_INIT_SIZE = 8

# Acceptor Class
class Acceptor():
	def __init__(self, ID, server_config):
		self.ID = ID
		self.server_config = server_config
		
		# IP/Port Configuration for this Acceptor
		self.IP = server_config[ID]["IP"]
		self.port = server_config[ID]["ACCEPTOR_PORT"]
		
		# Lock for reading/writing to arrays
		self.lock = _thread.allocate_lock()
		
		# Arrays for the status of each round (load from disk if they exit)
		self.filenames = {\
		"MAX_PREPARE_LIST" : "acceptor_{}_MPL.log".format(ID), \
		"ACC_NUM_LIST" : "acceptor_{}_ACL.log".format(ID),\
		"ACC_VAL_LIST" : "acceptor_{}_AVL.log".format(ID)}
		
		if self.files_exist():
			self.load_data()
		else:
			self.max_prepare_list = [None] * ARRAY_INIT_SIZE
			self.acc_num_list     = [None] * ARRAY_INIT_SIZE
			self.acc_val_list     = [None] * ARRAY_INIT_SIZE
		
		# Persistent Sending Socket
		self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
		
		# Start listening thread for incoming messages
		_thread.start_new_thread(self.listen, ())

		
	# Listen for incoming connections by binding to the socket specified in the hosts file
	def listen(self):
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			self.sock.bind((self.IP, self.port))
			while True:
				msg, source = self.sock.recvfrom(4096)
				
				# Process message on a thread
				_thread.start_new_thread(self.process_message, (msg, source,))
				
		except:
			# Restart listening thread
			_thread.start_new_thread(self.listen, ())
			
	# Process the received message
	def process_message(self, msg, source):
		msg = pickle.loads(msg)
		
		# Display Debug Information
		type = msg["TYPE"]
		s1 = "Server: [{}   {}]".format(self.ID, "ACCEPTOR")
		s2 = "Status: [{} {}]".format("RECEIVED", type)
		s3 = "Source:      [{}:{}]".format(source[0], source[1])
		print("{:<40} {:<40} {:<40}".format(s1, s2, s3))
		
		if type == "PROPOSE":
			slot = msg["SLOT"]
			n = msg["N"]
			if (self.get_max_prepare(slot) is None) or (n > self.get_max_prepare(slot)):
				self.set_max_prepare(slot, n)
				source = (source[0], self.server_config[msg["ID"]]["PROPOSER_PORT"])
				self.promise(slot, source)
		elif type == "ACCEPT":
			slot = msg["SLOT"]
			n = msg["N"]
			# Determine whether to send an ack message and update state
			if n >= self.get_max_prepare(slot):
				v = msg["EVENT"]
				self.set_acc_num(slot, n)
				self.set_acc_val(slot, v)
				self.set_max_prepare(slot, n)
				source = (source[0], self.server_config[msg["ID"]]["PROPOSER_PORT"])
				# Send an ack message
				self.ack(slot, source)
			
	def promise(self, slot, dest):
		acc_num = self.get_acc_num(slot)
		acc_val = self.get_acc_val(slot)
		msg = {"TYPE": "PROMISE", "SLOT": slot, "ACC_NUM": acc_num, "ACC_VAL": acc_val, "ID": self.ID}
		self.send_msg(dest[0], dest[1], msg)
		
		
	# Send an ack message
	def ack(self, slot, dest):
		acc_num, acc_val = self.get_acc_num(slot), self.get_acc_val(slot)
		msg = {"TYPE": "ACK", "SLOT": slot, "ACC_NUM": acc_num, "ACC_VAL": acc_val, "ID": self.ID}
		self.send_msg(dest[0], dest[1], msg)
			
	# Given a destination IP and port, send a message
	def send_msg(self, dest_ip, dest_port, message):
		try:
			# Display Debug Information
			s1 = "Server: [{}   {}]".format(self.ID, "ACCEPTOR")
			s2 = "Status: [{} {}]".format("SENDING", message["TYPE"])
			s3 = "Destination: [{}:{}]".format(dest_ip, dest_port)
			print("{:<40} {:<40} {:<40}".format(s1, s2, s3))
			
			# Send Message
			msg = pickle.dumps(message)
			self.send_sock.sendto(msg, (dest_ip, dest_port))
		except:
			pass
		
		
	def get_max_prepare(self, slot):
		with self.lock:
			# Return None if the slot is out of bounds (even definitely not present)
			if slot >= len(self.max_prepare_list):
				return None
			return self.max_prepare_list[slot]		
	
	
	def get_acc_num(self, slot):
		with self.lock:
			# Return None if the slot is out of bounds (even definitely not present)
			if slot >= len(self.acc_num_list):
				return None
			return self.acc_num_list[slot]
		
	def get_acc_val(self, slot):
		with self.lock:
			# Return None if the slot is out of bounds (even definitely not present)
			if slot >= len(self.acc_val_list):
				return None
			return self.acc_val_list[slot]
	
	# Given a slot and value, update the max prepare array
	def set_max_prepare(self, slot, n):
		with self.lock:
			while len(self.max_prepare_list) - 1 < slot:
				self.extend_max_prepare_list()
			self.max_prepare_list[slot] = n
			pickle.dump(self.max_prepare_list, open(self.filenames["MAX_PREPARE_LIST"], "wb" ))
		
	# Given a slot and value, update the acc num array
	def set_acc_num(self, slot, n):
		with self.lock:
			while len(self.acc_num_list) - 1 < slot:
				self.extend_acc_num_list()
			self.acc_num_list[slot] = n
			pickle.dump(self.max_prepare_list, open(self.filenames["ACC_NUM_LIST"], "wb" ))
		
	# Given a slot and value, update the acc val array
	def set_acc_val(self, slot, v):
		with self.lock:
			while len(self.acc_val_list) - 1 < slot:
				self.extend_acc_val_list()
			self.acc_val_list[slot] = v
			pickle.dump(self.max_prepare_list, open(self.filenames["ACC_VAL_LIST"], "wb" ))
			
	# Extend the Max Prepare list to twice it's size
	def extend_max_prepare_list(self):
		size = len(self.max_prepare_list)
		self.max_prepare_list.extend([None] * size)
		
	# Extend the Accepted Number list to twice it's size
	def extend_acc_num_list(self):
		size = len(self.acc_num_list)
		self.acc_num_list.extend([None] * size)
	
	# Extend the Accepted Value list to twice it's size
	def extend_acc_val_list(self):
		size = len(self.acc_val_list)
		self.acc_val_list.extend([None] * size)
		
	def files_exist(self):
		status = True
		for key in self.filenames:
			filename = self.filenames[key]
			if not os.path.isfile(filename):
				status = False
		return status
		
	def load_data(self):
		self.max_prepare_list = pickle.load(open(self.filenames["MAX_PREPARE_LIST"], "rb" ))
		self.acc_num_list = pickle.load(open(self.filenames["ACC_NUM_LIST"], "rb" ))
		self.acc_val_list = pickle.load(open(self.filenames["ACC_VAL_LIST"], "rb" ))
		
		