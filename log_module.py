import os, sys
from event_module import *
import _thread

ARRAY_INIT_SIZE = 8

# Log Class
class Log():
	def __init__(self, filename):
		self.filename = filename
		self.lock = _thread.allocate_lock()
	
		# Initialize log if no local copy exists, otherwise recover from file
		if os.path.isfile(self.filename):
			self.load_log()
		else:
			self.events_log = [None] * ARRAY_INIT_SIZE
		
		
	def load_log(self):
		pass
		
	def write(self, slot, event):
		username = event.get_username()
		operation = event.get_operation()
		with self.log_lock:
			pass # Write to file
		
	def get_entry(self, slot):
		return self.events_log[slot]
		
	def set_entry(self, slot, event):
		# Add event to in-memory data structure
		if len(self.events_log) - 1 < slot:
			self.extend_events_log()
		self.events_log[slot] = event
		
		# Add event to disk
		self.write(slot, event)
	
	def extend_events_log(self):
		size = len(self.events_log)
		self.events_log.extend([None] * size)
