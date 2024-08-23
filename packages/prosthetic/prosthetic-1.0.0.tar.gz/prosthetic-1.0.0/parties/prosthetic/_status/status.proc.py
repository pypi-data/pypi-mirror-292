

def add_paths_to_system (paths):
	import pathlib
	from os.path import dirname, join, normpath
	import sys
	
	this_folder = pathlib.Path (__file__).parent.resolve ()	
	for path in paths:
		sys.path.insert (0, normpath (join (this_folder, path)))

add_paths_to_system ([
	'/habitat/parties'
])


import prosthetic
from prosthetic._essence import retrieve_essence
import os
import subprocess
import pathlib
from os.path import dirname, join, normpath
import os
import sys

import Emergency

import rich

this_folder = pathlib.Path (__file__).parent.resolve ()
habitat = "/habitat"
relative_path = str (normpath (join (habitat, "parties/prosthetic")))
constellations = str (normpath (join (this_folder, "constellations")))

def turn_on_the_venture ():
	essence = retrieve_essence ()
	medify_process_path = essence ["glossary"] ["prosthetic"]
	assert (type (medify_process_path) == str)	
	assert (len (medify_process_path) >= 1)
	
	process = subprocess.Popen ([
		medify_process_path,
		"ventures",
		"on"
	])
	
def turn_off_the_venture ():
	essence = retrieve_essence ()
	medify_process_path = essence ["glossary"] ["prosthetic"]
	assert (type (medify_process_path) == str)	
	assert (len (medify_process_path) >= 1)
	
	process = subprocess.Popen ([
		medify_process_path,
		"ventures",
		"off"
	])

os.chdir (constellations)

turn_on_the_venture ()







if (len (sys.argv) >= 2):
	glob_string = relative_path + '/' + sys.argv [1]
else:
	glob_string = relative_path + '/**/monitor_*.py'




this_directory = pathlib.Path (__file__).parent.resolve ()
monitors_path = str (normpath (join (this_directory, f"monitors")))

promote = Emergency.on ({
	"glob_string": glob_string,
	"simultaneous": True,
	"simultaneous_capacity": 50,
	"time_limit": 60,
	"module_paths": [
		normpath (join (habitat, "parties"))
	],
	"relative_path": relative_path,
	"db_directory": normpath (join (this_directory, "DB")),
	"aggregation_format": 2
})

promote ["off"] ()

#
#	This is a detailed report
#	of the technique.
#
rich.print_json (data = {
	"paths": promote ["proceeds"] ["paths"]
})

#
#	This is the checks that did 
#	not finish successfully.
#
rich.print_json (data = {
	"alarms": promote ["proceeds"] ["alarms"]
})

#
#	This is concise stats about
#	the  technique.
#
rich.print_json (data = {
	"stats": promote ["proceeds"] ["stats"]
})


turn_off_the_venture ()

#
#
#