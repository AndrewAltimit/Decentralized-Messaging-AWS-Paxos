import socket
import _thread
import os, sys
import pickle
from event_module import *
import time

# Initial array sizes, double as needed for each reallocation
ARRAY_INIT_SIZE = 8

# Max amount of time allowed for expected incoming messages
TIMEOUT = 1.5

# Time between each garbage collection procedure on the message buffer (remove expired messages)
GARBAGE_COLLECT_FREQ = TIMEOUT * 3

# Proposer Class
class Proposer():
	def __init__(self, ID, server_config, log):
		self.ID = ID
		self.log = log
		self.server_config = server_config
		
		# IP/Port Configuration for this Proposer
		self.IP = server_config[ID]["IP"]
		self.port = server_config[ID]["PROPOSER_PORT"]
		
		# Array of known leaders
		self.leader_list = [None] * ARRAY_INIT_SIZE
		
		# Array of event counts for each slot (n)
		self.event_counter = [0] * ARRAY_INIT_SIZE
		
		# Majority Size
		self.majority_size = (len(server_config.keys()) // 2) + 1
		
		# Message Buffer
		self.message_buffer = []
		
		# Start listening thread for incoming messages
		_thread.start_new_thread(self.listen, ())
		
		# Start garbage collection thread for message buffer
		_thread.start_new_thread(self.message_buffer_garbage_collector, ())
		
	# Listen for incoming connections by binding to the socket specified in the hosts file
	def listen(self):
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			self.sock.bind((self.IP, self.port))
			while True:
				msg, source = self.sock.recvfrom(4096)
				self.process_message(msg, source)
				
		except:
			# Restart listening thread
			_thread.start_new_thread(self.listen, ())
			
			
	# Process the received message
	def process_message(self, msg, source):
		msg = pickle.loads(msg)

		# received timestamp in order to remove expired messages later on
		recv_timestamp = time.time()
		
		# Add message to the buffer
		self.message_buffer.append((recv_timestamp, msg))
		
		# Display Debug Information
		type = msg["TYPE"]
		s1 = "Server: [{}   {}]".format(self.ID, "PROPOSER")
		s2 = "Status: [{} {}]".format("RECEIVED", type)
		s3 = "Source:      [{}:{}]".format(source[0], source[1])
		print("{:<40} {:<40} {:<40}".format(s1, s2, s3))
		
	# Return True/False if the event was successfully inserted into the latest available slot
	def insert_event(self, event):
		# Get next available slot
		slot = self.log.get_next_available_slot()
		print("Trying to fill in this slot:", slot)
		
		# Send proposal
		self.increment_event_counter()
		n = (self.event_counter[slot],self.ID)
		self.propose(slot, n)
		
		# Wait for Promise Messages
		current_time = time.time()
		while ((time.time() - current_time) < TIMEOUT) and (len(self.get_promises(slot)) < self.majority_size):
			time.sleep(.01)
		responses = self.get_promises(slot)
		
		# If not enough responses received, return False as the insertion failed
		if len(responses) < self.majority_size:
			return False
		
		# Filter out responses with null values
		responses = list(filter(lambda x: (x[0] is not None) and (x[1] is not None), responses))
		
		# Determine v to use
		if len(responses) == 0:
			v = event
		else:
			responses.sort(key=lambda x: x[0])
			v = responses[0][1] 
			
		# Send accept message
		self.accept(slot, n, v) 
		
		# Wait for ACK Messages
		current_time = time.time()
		while ((time.time() - current_time) < TIMEOUT) and (len(self.get_acks(slot)) < self.majority_size):
			time.sleep(.01)
		responses = self.get_acks(slot)
		
		# If not enough responses received, return False as the insertion failed
		if len(responses) < self.majority_size:
			return False
		
		# Send commit message
		self.commit(slot, v)
		
		# Return True / False depending on whether the value commited 
		# was the original event we were trying to insert
		
		return v == event
		
		
	# Send propose message to all acceptors
	def propose(self, slot, n):
		msg = {"TYPE": "PROPOSE", "SLOT": slot, "N": n}
		self.send_all_acceptors(msg)
		
	# Send accept message to all acceptors
	def accept(self, slot, n, event):
		msg = {"TYPE": "ACCEPT", "SLOT": slot, "N": n, "EVENT": event}
		self.send_all_acceptors(msg)
		
	# Send commit message to all learners for a particular slot and event
	def commit(self, slot, event):
		msg = {"TYPE": "COMMIT", "SLOT": slot, "EVENT": event}
		self.send_all_learners(msg)
		
	# Return all promises on the message queue which correspond to slot
	def get_promises(self, slot):
		promises = []
		for timestamp, msg in self.message_buffer:
			if (msg["TYPE"] == "PROMISE") and (msg["SLOT"] == slot):
				promises.append((msg["ACC_NUM"], msg["ACC_VAL"]))
		return promises
		
	# Return all acks on the message queue which correspond to slot
	def get_acks(self, slot):
		acks = []
		for timestamp, msg in self.message_buffer:
			if (msg["TYPE"] == "ACK") and (msg["SLOT"] == slot):
				acks.append((msg["ACC_NUM"], msg["ACC_VAL"]))
		return acks
		
	# Search the log for gaps of knowledge. Fill these in with Synod Algorithm
	def fill_holes(self):
		pass
		
	# Attempt to learn newer entries beyond the latest known log entry
	def update_log(self):
		pass
	
	# Return True/False if self is the leader for a given slot
	def isLeader(self, slot):
		return (getLeader(slot) == self.ID)
		
	# Get the known leader (if any) for a particular slot
	# None is returned if no known leader exists
	def getLeader(self, slot):
		return self.leader_list[slot]
		
	# Set the known leader for a particular slot
	def setLeader(self, slot, ID):
		while len(self.leader_list) - 1 < slot:
			self.extend_leader_list()
		self.leader_list[slot] = ID
		
	# Extend the leader list to twice it's size
	def extend_leader_list(self):
		size = len(self.leader_list)
		self.leader_list.extend([None] * size)
		
	# Increment event counter for a particular slot
	def increment_event_counter(self, slot, ID):
		while len(self.event_counter) - 1 < slot:
			self.extend_event_counter_list()
		self.event_counter[slot] += 1
		
	# Extend the event counter list to twice it's size
	def extend_event_counter_list(self):
		size = len(self.event_counter)
		self.event_counter.extend([0] * size)
		
		
	# Given a destination IP and port, send a message
	def send_msg(self, dest_ip, dest_port, message):
		try:
			# Display Debug Information
			s1 = "Server: [{}   {}]".format(self.ID, "PROPOSER")
			s2 = "Status: [{} {}]".format("SENDING", message["TYPE"])
			s3 = "Destination: [{}:{}]".format(dest_ip, dest_port)
			print("{:<40} {:<40} {:<40}".format(s1, s2, s3))
			
			# Send Message
			msg = pickle.dumps(message)
			self.sock.sendto(msg, (dest_ip, dest_port))
		except:
			pass
			
	# Send message to all proposers (including self) -> Used for debug purposes
	def send_all_proposers(self, message):
		for ID in self.server_config:
			dest_ip = self.server_config[ID]["IP"]
			dest_port = self.server_config[ID]["PROPOSER_PORT"]
			self.send_msg(dest_ip, dest_port, message)
		
	# Send message to all acceptors
	def send_all_acceptors(self, message):
		for ID in self.server_config:
			dest_ip = self.server_config[ID]["IP"]
			dest_port = self.server_config[ID]["ACCEPTOR_PORT"]
			self.send_msg(dest_ip, dest_port, message)
			
	# Send message to all learners		
	def send_all_learners(self, message):
		for ID in self.server_config:
			dest_ip = self.server_config[ID]["IP"]
			dest_port = self.server_config[ID]["LEARNER_PORT"]
			self.send_msg(dest_ip, dest_port, message)
			
	# Garbage Collection for Message Buffer
	def message_buffer_garbage_collector(self):
		while True:
			# Remove expired messages from the front of the queue
			current_time = time.time()
			while (len(self.message_buffer) > 0) and (current_time - self.message_buffer[0][0] > TIMEOUT):
				self.message_buffer.pop(0)
			# Wait before running garbage collection again	
			time.sleep(GARBAGE_COLLECT_FREQ)