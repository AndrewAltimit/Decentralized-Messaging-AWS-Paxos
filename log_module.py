import os, sys
from event_module import *
import _thread
import pickle


ARRAY_INIT_SIZE = 8

# Log Class
class Log():
	def __init__(self, ID, username):
		self.ID = ID
		self.filenames = {\
		"LOG" : "server_{}_log.log".format(ID), \
		"TIMELINE" : "server_{}_timeline.log".format(ID),\
		"BLOCKLIST" : "server_{}_blocklist.log".format(ID),}
		self.lock = _thread.allocate_lock()
		self.username = username
		self.checkpoint = 0
	
		# Initialize log, timeline, and block list
		self.events_log = [None] * ARRAY_INIT_SIZE
		self.timeline = []
		self.blocks = set()
		
		# Recover from files if they exist
		if os.path.isfile(self.filenames["TIMELINE"]):
			self.timeline = pickle.load(open(self.filenames["TIMELINE"], "rb" ))
		if os.path.isfile(self.filenames["BLOCKLIST"]):
			self.blocks = pickle.load(open(self.filenames["BLOCKLIST"], "rb" ))
		if os.path.isfile(self.filenames["LOG"]):
			self.load_log()
		
		print("Checkpoint Status:", self.checkpoint)
			
		
		
	def load_log(self):
		# open the file of current server for write
		f = open(self.filenames["LOG"], 'rb')
		
		replay_events = []
		while True:
			# unpickle each pickle container until reach the end
			try:
				slot, event = pickle.load(f)
				self.checkpoint += 1
				if self.checkpoint % 5 == 0:
					replay_events = []
				else:
					replay_events.append(event)
				

				# extend events_log when needed
				while len(self.events_log) - 1 < slot:
					self.extend_events_log()
				self.events_log[slot] = event

			except EOFError:
				break
		f.close()
		
		# Replay events (up to 4 of the latest events from the log file)
		self.replay(replay_events)
		
	def replay(self, events):
		print("[LOG] Replaying {} events...".format(len(events)))
		for event in events:
			self.process_event_internally(event)
		print("[LOG] Finished replaying events")
		
	def write(self, slot, event):			
		with self.lock:
			# Write to file
			# open the file of current server for write in append mode
			f = open(self.filenames["LOG"], 'ab')
			# write in (slot, event_obj)
			pickle.dump((slot,event), f)
			f.close()
			
			

				
	def store_timeline(self):
		with self.lock:
			pickle.dump(self.timeline, open(self.filenames["TIMELINE"], "wb" ))
	
				
	def store_blocklist(self):
		with self.lock:
			pickle.dump(self.blocks, open(self.filenames["BLOCKLIST"], "wb" ))


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
		
		# Add event to in-memory data structure
		self.process_event_internally(event)
		
		# Increment and potentially store checkpoints
		self.increment_checkpoint()
		if self.checkpoint % 5 == 0:
			self.store_timeline()
			self.store_blocklist()
		
			
	def process_event_internally(self, event):
		# Event Type Procedure:
		# Tweet       -> Add to Timeline
		# InsertBlock -> Add to block list
		# DeleteBlock -> Remove from block list
		if type(event) == Tweet:
			self.timeline.append(event)
		elif type(event) == InsertBlock:
			self.blocks.add(event)
		elif type(event) == DeleteBlock:
			self.blocks -= set([event.convert_to_IB()])
			
	
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
		output = "{:-^120}\n".format("TIMELINE")
		for event in sorted(self.timeline, reverse = True):
			if self.is_viewable(event):
				output += str(event) + "\n"
		output += "-" * 120
		print(output)
		
	def view_log(self):
		output = "{:-^120}\n".format("LOG CONTENTS")
		for i in range(len(self.events_log)):
			output += "SLOT {}: {}\n".format(i + 1, str(self.events_log[i]))
		output += "-" * 120
		print(output)
	
	def view_blocklist(self):
		output = "{:-^120}\n".format("BLOCK LIST")
		for block in self.blocks:
			output += str(block) + "\n"
		output += "-" * 120
		print(output)
	
	def increment_checkpoint(self):
		self.checkpoint += 1
