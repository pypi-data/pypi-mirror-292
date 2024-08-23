


from prosthetic._essence import retrieve_essence
import law_dictionary
import subprocess
def the_process (params):
	law_dictionary.check (	
		allow_extra_fields = True,
		laws = {
			"DB_directory": {
				"required": True,
				"type": str
			},
			"port": {
				"required": True,
				"type": str
			},
			"CWD": {
				"required": True,
				"type": str
			},
			"PID_file_path": {
				"required": True,
				"type": str
			},
			"log_file_path": {
				"required": True,
				"type": str
			}
		},
		dictionary = params
	)

	port = params ["port"]
	DB_directory = params ["DB_directory"]
	CWD = params ["CWD"]
	PID_file_path = params ["PID_file_path"]
	log_file_path = params ["log_file_path"]

	subprocess.run (
		f"mongod --fork --dbpath '{ DB_directory }' --port '{ port }' --pidfilepath '{ PID_file_path }' --logpath '{ log_file_path }'", 
		shell = True, 
		check = True,
		cwd = CWD
	)
	
	rich.print_json (data = {
		"mongo node": "started"
	})

	return;

from multiprocessing import Process
import rich
import os
from prosthetic._essence import retrieve_essence
	

def turn_on ():
	essence = retrieve_essence ()
	

	mongo_essence = prosthetic_essence.find ("mongo")
	PID_file_path = mongo_essence ["PID_file_path"]
	log_file_path = mongo_essence ["log_file_path"]
	
	os.makedirs(os.path.dirname(PID_file_path), exist_ok=True)
	os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
	
	edited_config = prosthetic_essence.find ("edited_config")

	rich.print_json (data = {
		"mongo": mongo_essence,
		"edited_config": edited_config
	})
	

	'''
	return;
	mongo_DB_directory = move ["mongo directory"]
	mongo_port = move ["mongo port"]
	'''

	nodes = edited_config ["trends"] ["nodes"]
	for node in nodes:
		mongo = Process (
			target = the_process,
			args = (),
			kwargs = {
				"params": {
					"CWD": edited_config ["CWD"], 
					"DB_directory": node ["data path"],
					"port": str (node ["port"]),
					"PID_file_path": PID_file_path,
					"log_file_path": log_file_path
				}
			}
		)
		
		mongo.start ()


	