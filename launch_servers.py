import os, sys
import pickle
import log_module
import proposer_module
import acceptor_module
import learner_module
from event_module import *
import time

# Given a hosts file path, parse out server information and store internally in a dictionary
# Dictionary: Stores all server connection info
# Key    =>  Server ID
# Value  =>  (IP, port, username)
def parse_config(hosts_file):
	ID = 1
	all_servers = dict()
	file = open(hosts_file)
	for line in file:
		if line.strip() == "":
			continue
		parsed_config = line.strip().split(" ")

		server_dict = dict()
		server_dict["IP"] = parsed_config[0]
		server_dict["USERNAME"] = parsed_config[1].title()
		server_dict["PROPOSER_PORT"] = int(parsed_config[2])
		server_dict["ACCEPTOR_PORT"] = int(parsed_config[3])
		server_dict["LEARNER_PORT"] = int(parsed_config[4])
		all_servers[ID] = server_dict
		ID+=1
	file.close()
	return all_servers

# Show all known server configurations
def show_server_config(all_servers):
	print("\n{:-^120}".format("SERVER CONFIGURATIONS"))
	for ID in all_servers:
		username = all_servers[ID]["USERNAME"]
		IP = all_servers[ID]["IP"]
		p_port = all_servers[ID]["PROPOSER_PORT"]
		a_port = all_servers[ID]["ACCEPTOR_PORT"]
		l_port = all_servers[ID]["LEARNER_PORT"]
		print("ID: {:<3} Username: {:<10} IP: {:<15} Proposer Port: {:<10} Acceptor Port: {:<10} Learner Port: {:<10}".format(ID, username, IP, p_port, a_port, l_port))
	print("-" * 120)

# Show all valid commands
def show_commands(valid_commands):
	print("\n{:-^120} ".format("COMMANDS"))
	print("{:^120} ".format("   ".join(valid_commands)))
	print("-" * 120)


### Message Sending Test ###
def message_test(proposer):
	message = {"TYPE": "TEST"}
	print("\n{:-^120} ".format("MESSAGE SENDING TEST"))
	# Sending to all proposers
	print("PROPOSER SENDING TO ALL PROPOSERS...")
	proposer.send_all_proposers(message)
	time.sleep(0.5)

	# Sending to all acceptors
	print("\nPROPOSER SENDING TO ALL ACCEPTORS...")
	proposer.send_all_acceptors(message)
	time.sleep(0.5)

	# Sending to all learners
	print("\nPROPOSER SENDING TO ALL LEARNERS...")
	proposer.send_all_learners(message)
	time.sleep(0.5)
	print("-" * 120)

if __name__ == "__main__":
	# Check if all proper input arguments exist
	if len(sys.argv) != 3:
		print("Improper number of input arguments")
		print("USAGE: launch_servers.py <Host ID> <Network Hosts File>")
		sys.exit()

	# Read in command line arguments
	server_ID = int(sys.argv[1])
	hosts_filename = sys.argv[2]

	# Parse Config File
	all_servers = parse_config(hosts_filename)
	show_server_config(all_servers)

	# Extract username for this server
	username = all_servers[server_ID]["USERNAME"]

	# Initialize the log
	log = log_module.Log(server_ID, all_servers, username)

	# Create proposer, acceptor, and learner
	#proposer = proposer_module.Proposer(server_ID, all_servers, log)
	acceptor = acceptor_module.Acceptor(server_ID, all_servers)
	learner = learner_module.Learner(server_ID, all_servers, log)

	# Message Sending Test
	# message_test(proposer)

	proposer.update_log()

	# Servers should remain active during the life of the program
	while True:
		time.sleep(100)
