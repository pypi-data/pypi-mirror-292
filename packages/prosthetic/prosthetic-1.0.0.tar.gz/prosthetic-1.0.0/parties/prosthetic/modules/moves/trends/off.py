


import os
from prosthetic._essence import retrieve_essence


def turn_off ():
	mongo_essence = prosthetic_essence.find ("mongo")
	PID_file_path = mongo_essence ["PID_file_path"]

	with open (PID_file_path, "r") as f:
		pid = int (f.read ().strip ())

	try:
		os.kill(pid, 15)
		print ("Mongo is off.")
		return;
		
	except OSError as e:
		print (f"Failed to stop Mongo: {e}")
		
	print ("An exception occurred")


