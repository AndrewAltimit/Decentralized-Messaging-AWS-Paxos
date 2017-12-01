import os, sys
from event_module import *
import _thread
import pickle


ARRAY_INIT_SIZE = 8

# Log Class
class Log():
	def __init__(self, filename, username):
		self.filename = filename
		self.lock = _thread.allocate_lock()
		self.username = username
	
		# Initialize log if no local copy exists, otherwise recover from file
		self.events_log = [None] * ARRAY_INIT_SIZE
		if os.path.isfile(self.filename):
			self.load_log()
			
		self.timeline = []
		self.blocks = set()
		self.create_timeline()
		self.create_blocking_set()
			
		
		
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
		with self.lock:
			# Write to file
			# open the file of current server for write in append mode
			f = open(self.filename, 'ab')
			# write in (slot, event_obj)
			pickle.dump((slot,event), f)
			f.close()
			
			
	# Create a timeline from the in-memory events log
	def create_timeline(self):
		for entry in self.events_log:
			if entry is None:
				continue
				
			if type(entry) == Tweet:
				self.timeline.append(entry)
				
	def create_blocking_set(self):
		for entry in self.events_log:
			if entry is None:
				continue
				
			if type(entry) == InsertBlock:
				self.blocks.add(entry)
			elif type(entry) == DeleteBlock:
				self.blocks.remove(entry.convert_to_IB())


		
	def get_entry(self, slot):
		# Return None if the slot is outside of log bounds (even definitely not present)
		if slot >= len(self.events_log):
			return None
		return self.events_log[slot]
		
	def set_entry(self, slot, event):
		# Do not write to the log if it is already present
		if self.get_entry(slot) is not None:
			return
			
		print("[LOG] Adding entry -> {}".format(str(event)))
			
		# Add event to in-memory data structure
		while len(self.events_log) - 1 < slot:
			self.extend_events_log()
		self.events_log[slot] = event
		
		# Add event to disk
		self.write(slot, event)
		
		# Event Type Procedure:
		# Tweet       -> Add to Timeline
		# InsertBlock -> Add to block list
		# DeleteBlock -> Remove from block list
		if type(event) == Tweet:
			self.timeline.append(event)
		elif type(event) == InsertBlock:
			self.blocks.add(event)
		elif type(event) == DeleteBlock:
			self.blocks.remove(event.convert_to_IB())
	
	def extend_events_log(self):
		size = len(self.events_log)
		self.events_log.extend([None] * size)
		
	# Return the next available slot (slot after last filled entry)
	def get_next_available_slot(self):
		for i in range(len(self.events_log) - 1, -1, -1):
			if self.events_log[i] is not None:
				return i + 1
		return 0
		
	def is_viewable(self, event):
		for block in self.blocks:
			# If the event username matches an InsertBlock initiator, is our user the blockee?
			if (event.username == block.username) and (block.follower == self.username):
				return False
		return True
		
	def view_timeline(self):
		print("{:-^120}".format("TIMELINE"))
		for event in sorted(self.timeline, reverse = True):
			if self.is_viewable(event):
				print(event)
		print("-" * 120)
