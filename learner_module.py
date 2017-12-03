import socket
import _thread
import os, sys, traceback
import pickle
import time
from event_module import *

# Learner Class
class Learner():
	def __init__(self, ID, server_config, log):
		self.ID = ID
		self.server_config = server_config
		self.log = log

		# IP/Port Configuration for this Learner
		self.IP = server_config[ID]["IP"]
		self.port = server_config[ID]["LEARNER_PORT"]

		# Number of messages for the listening thread to drop (used for debug purposes)
		self.drop_counter = 0

		# Persistent Sending Socket
		self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

		# Start listening thread for incoming messages
		_thread.start_new_thread(self.listen, ())


	# Listen for incoming connections by binding to the socket specified in the hosts file
	def listen(self):
		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			self.sock.bind(('', self.port))
			while True:
				msg, source = self.sock.recvfrom(4096)

				# Drop messages if requested to by the user
				if self.drop_counter > 0:
					self.drop_counter -= 1
					continue

				# Process message on a thread
				_thread.start_new_thread(self.process_message, (msg, source,))

		except:
			traceback.print_exc(file=sys.stdout)
			# Restart listening thread
			_thread.start_new_thread(self.listen, ())

	# Process the received message
	def process_message(self, msg, source):
		msg = pickle.loads(msg)

		# Display Debug Information
		msg_type = msg["TYPE"]
		s1 = "Server: [{}   {}]".format(self.ID, " LEARNER")
		s2 = "Status: [{} {}]".format("RECEIVED", msg_type)
		s3 = "Source:      [{}:{}]".format(source[0], source[1])
		print("{:<40} {:<40} {:<40}".format(s1, s2, s3))

		# If the received message is a commit message, pass it to the log
		if msg_type == "COMMIT":
			slot = msg["SLOT"]
			event = msg["EVENT"]
			self.log.set_entry(slot, event)

	# Given a destination IP and port, send a message
	def send_msg(self, dest_ip, dest_port, message):
		try:
			# Display Debug Information
			s1 = "Server: [{}   {}]".format(self.ID, " LEARNER")
			s2 = "Status: [{} {}]".format("SENDING", message["TYPE"])
			s3 = "Destination: [{}:{}]".format(dest_ip, dest_port)
			print("{:<40} {:<40} {:<40}".format(s1, s2, s3))

			# Send Message
			msg = pickle.dumps(message)
			self.send_sock.sendto(msg, (dest_ip, dest_port))
		except:
			pass

	# Drop the requested number of messages in the listening thread
	def drop_messages(self, num_messages):
		self.drop_counter = num_messages
