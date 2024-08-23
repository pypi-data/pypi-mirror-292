
'''
	from prosthetic.monetary.ingredients.DB.off import turn_off_monetary_node
	mongo_process = turn_off_monetary_node ()
'''

'''
	mongod --shutdown --pidfilepath /var/run/mongodb/mongod.pid
'''

#/
#
from prosthetic._essence import retrieve_essence
#
#
from ventures.utilities.hike_passive_forks import hike_passive_forks
#
#
import multiprocessing
import subprocess
import time
import os
import atexit
#
#\


def turn_off_monetary_node (
	exception_if_off = False
):
	essence = retrieve_essence ()


	if (essence ["trends"] ["monetary"] ["node"] ["local"] == "yes"):
		monetary_node = essence ["trends"] ["monetary"] ["node"]
	
		dbpath = monetary_node ["data_path"]
		PID_path = monetary_node ["PID_path"]

		hike_passive_forks ({
			"script": " ".join ([
				"mongod",
				"--shutdown",
				
				'--dbpath', 
				f"{ dbpath }", 
				
				"--pidfilepath",
				f"'{ PID_path }'"
			]),
			"Popen": {
				#"cwd": harbor_path,
				#"env": env_vars,
				"shell": True
			}
		})
	
	return;