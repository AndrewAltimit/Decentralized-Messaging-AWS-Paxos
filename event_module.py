import time as time_mod
import calendar

# Tweet Object
class Tweet():
	def __init__(self, username, message):
		self.username = username
		self.message = message
		self.utc_time = time_mod.asctime(time_mod.gmtime())
		
		
	# Return string representation of a tweet object
	def __str__(self):
		return "{:<23} | {}: {}".format(self.utc_to_local(), self.username, self.message)
		
	# Return the hash for a Tweet object
	def __hash__(self):
		return hash("{}::{}::{}".format(self.username, self.message, self.utc_time))
		
	# Order tweets by UTC time
	def __lt__(self, other):
		return self.utc_time < other.utc_time
		
	# Determine if two Tweet objects are the same
	def __eq__(self, other):
		return isinstance(other, Tweet) and (self.username == other.username and self.message == other.message and self.utc_time == other.utc_time)
		
	# converts from UTC time to local time on this machine
	def utc_to_local(self):
		# get the time struct from the formatted string
	    utc_struct = time_mod.strptime(self.utc_time, '%a %b %d %H:%M:%S %Y')
		
	    # convert this time struct to seconds since epoch time
	    utc_seconds = calendar.timegm(utc_struct)
		
	    # convert these seconds to our local time
	    loc_struct = time_mod.localtime(utc_seconds)
		
	    return time_mod.asctime(loc_struct)
		
	# Return whether self is a certain object type
	def is_type(self, object_type):
		return type(self) is object_type
		
	# Return self since already unpacked
	def unpack(self):
		return self

		
# Insert Block Object
class InsertBlock():
	# username = user who initiated block
	# follower = user who is blocked
	def __init__(self, username, follower):
		self.username = username
		self.follower = follower
		
	# Return string representation of a insert block object
	def __str__(self):
		return "{} blocking {}".format(self.username, self.follower)
		
	# Return the hash for a InsertBlock object
	def __hash__(self):
		return hash("{}::BLOCK::{}".format(self.username, self.follower))
		
	# Determine if two InsertBlock objects are the same
	def __eq__(self, other):
		return isinstance(other, InsertBlock) and (self.username == other.username and self.follower == other.follower)
		
	# Return whether self is a certain object type
	def is_type(self, object_type):
		return type(self) is object_type
		
	# Return self since already unpacked
	def unpack(self):
		return self
		
# Delete Block Object
class DeleteBlock():
	# username = user who initiated block
	# follower = user who is being unblocked
	def __init__(self, username, follower):
		self.username = username
		self.follower = follower
		
	# Return string representation of a insert block object
	def __str__(self):
		return "{} unblocking {}".format(self.username, self.follower)
		
	# Return the hash for a DeleteBlock object
	def __hash__(self):
		return hash("{}::UNBLOCK::{}".format(self.username, self.follower))
		
	# Determine if two DeleteBlock objects are the same
	def __eq__(self, other):
		return isinstance(other, DeleteBlock) and (self.username == other.username and self.follower == other.follower)
		
	# Return whether self is a certain object type
	def is_type(self, object_type):
		return type(self) is object_type
		
	# Return self since already unpacked
	def unpack(self):
		return self


# Event Record Class
class EventRecord():
	# Possible OP types: Tweet, InsertBlock, DeleteBlock
	def __init__(self, operation, time, node):
		self.op = operation
		self.time = int(time)
		self.node = int(node)
		

	# Return a string representation of the event record
	def __str__(self):
		return "Node: {:<2} Time: {} OP: {} -> {} ".format(self.node  + 1, self.time, self.get_formatted_type(), str(self.op))

	# Given two event records, determine whether they are equal or not
	# Note that we stricly use the operation, the time (lamport timestamp), and source node. No two unique events should share these
	def __eq__(self, other):
		return isinstance(other, EventRecord) and (self.op == other.op and self.time == other.time and self.node == other.node)

	# Return the hash for an event record object
	# Hashed from a unique identifier
	def __hash__(self):
		return hash("{}::{}::{}".format(hash(self.op), self.node, self.time))

	# Return OP object type
	def get_type(self):
		return type(self.op)
		
	# Return the operation for this event record
	def get_operation(self):
		return self.op
		
	# Return the username which created this event record
	def get_username(self):
		return self.op.username
		
	# Return OP object type as a formatted string
	def get_formatted_type(self):
		object_type = str(self.get_type()).split(".")[-1]
		return object_type.split("'")[0]
		
	# Return whether OP is a certain object type
	def is_type(self, object_type):
		return self.get_type() is object_type
		
	# Unpack EventRecord (as an operation)
	def unpack(self):
		return self.op
		
		

