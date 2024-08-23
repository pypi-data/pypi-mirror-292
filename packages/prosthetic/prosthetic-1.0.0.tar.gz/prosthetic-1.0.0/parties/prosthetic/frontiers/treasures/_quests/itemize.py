
'''
	from prosthetic.frontiers.treasures._quests.enumerate import enumerate_treasures
	treasures = enumerate_treasures ()
'''


import os
from prosthetic._essence import retrieve_essence

from pprint import pprint

def list_directories (directory):
	directories = []
	anomalies = []

	places = os.listdir (directory)
	for place in places:
		full_path = os.path.join (directory, place)
		
		if (os.path.isdir (full_path)):
			directories.append (place)
		else:
			raise Exception (f"A non-directory was found at: { place }")

	return {
		"directories": directories,
		"anomalies": anomalies
	}
	
def split_last_substring (string):
	last_dot_index = string.rfind ('.')

	if last_dot_index != -1:
		part_before = string [:last_dot_index]
		part_after = string [last_dot_index + 1:]
		return [ part_before, part_after ]
	
	raise Exception (f"A non-dot directory name was found: { string }")

def itemize_treasures (packet = {}):
	essence = retrieve_essence ()
	treasures_path = essence ["treasures"] ["path"]

	print_to_shell = "no"
	if (type (packet) == dict):
		if ("print_to_shell" in packet):
			print_to_shell = packet ["print_to_shell"]

	proceeds = list_directories (treasures_path)
	directories = proceeds ["directories"]
	anomalies = proceeds ["anomalies"]
	
	treasures = []
	for directory in directories:
		#print ("directory:", directory)
		
		print ("directory:", directory)
		
		domain_split = split_last_substring (directory)
		treasures.append ({
			"domain": directory,
			"domain split": domain_split,
		})
		
		
	if (print_to_shell == "yes"):
		pprint (treasures)	
		


	return treasures