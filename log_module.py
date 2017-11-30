import os, sys
from event_module import *
import _thread
import pickle


ARRAY_INIT_SIZE = 8

# Log Class
class Log():
	def __init__(self, filename):
		self.filename = filename
		self.lock = _thread.allocate_lock()
	
		# Initialize log if no local copy exists, otherwise recover from file
		self.events_log = [None] * ARRAY_INIT_SIZE
		if os.path.isfile(self.filename):
			self.load_log()
		
		
	def load_log(self):
		# open the file of current server for write, hardcoded as 1
		f = open(self.filename, 'rb')
		
		while True:
			# unpickle each pickle container until reach the end
		    try:
		        slot, event = pickle.load(f)

		        # extend events_log when needed
		        while len(self.events_log) - 1 < slot:
		        	self.extend_events_log()
		        self.events_log[slot] = event

		    except EOFError:
		        break

		f.close()
		
		
	def write(self, slot, event):
		# Do not write to the log if it is already present
		if self.get_entry(slot) is not None:
			return
			
		with self.lock:
			# Write to file
			# open the file of current server for write in append mode
			f = open(self.filename, 'ab')
			# write in (slot, event_obj)
			pickle.dump((slot,event), f)
			f.close()


		
	def get_entry(self, slot):
		# Return None if the slot is outside of log bounds (even definitely not present)
		if slot >= len(self.events_log):
			return None
		return self.events_log[slot]
		
	def set_entry(self, slot, event):
		# Add event to in-memory data structure
		while len(self.events_log) - 1 < slot:
			self.extend_events_log()
		self.events_log[slot] = event
		
		# Add event to disk
		self.write(slot, event)
	
	def extend_events_log(self):
		size = len(self.events_log)
		self.events_log.extend([None] * size)
		
	# Return the next available slot (slot after last filled entry)
	def get_next_available_slot(self):
		for i in range(len(self.events_log) - 1, -1, -1):
			if self.events_log[i] is not None:
				return i + 1
		return 0
