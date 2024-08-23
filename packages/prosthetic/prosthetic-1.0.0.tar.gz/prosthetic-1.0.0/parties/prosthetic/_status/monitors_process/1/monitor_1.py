


import prosthetic
from prosthetic._essence import retrieve_essence
import os
import subprocess





def check_1 ():
	essence = retrieve_essence ()
	medify_process_path = essence ["glossary"] ["prosthetic"]
	assert (type (medify_process_path) == str)	
	assert (len (medify_process_path) >= 1)
	
	print ("medify_process_path:", medify_process_path)
	
	return;
	
	process = subprocess.Popen ([
		medify_process_path,
		"ventures",
		"on"
	])
	
	return;
	
	
checks = {
	'check 1': check_1
}