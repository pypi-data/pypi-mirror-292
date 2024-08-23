

''''

"'''


#/
#
from prosthetic._essence import retrieve_essence
import prosthetic.mixes.procedure as procedure
#
#
import click
import rich
#
#
import pathlib
from os.path import dirname, join, normpath
import sys
import os
import time
#
#\


def import_documents (packet):
	version = packet ["version"]
	drop = packet ["drop"]

	print ("drop:", drop)

	essence = retrieve_essence ()

	essence = retrieve_essence ()
	the_exports_path = essence ["trends"] ["monetary"] ["saves"] ["exports"] ["path"]
	URL = essence ["trends"] ["monetary"] ["URL"]
	monetary_databases = essence ["trends"] ["monetary"] ["saves"] ["exports"] ["databases"]
	
	not_found = []
	for monetary_database in monetary_databases:
		database_name = monetary_databases [ monetary_database ] ["alias"]
		database_collections = monetary_databases [ monetary_database ] ["collections"]
		
		for collection in database_collections:
			name = collection + ".export"
			export_path = str (normpath (join (
				the_exports_path, 
				version,
				database_name, 
				name
			)))
			if (os.path.exists (export_path) != True):
				not_found.append (export_path)
				continue;
			
			script = [
				"mongoimport",
				"--uri",
				URL,
				f"--db={ database_name }",
				f"--collection={ collection }",
				f"--file={ export_path }"
			]
			if (drop):
				script.append ('--drop')
				
			procedure.go (
				script = script
			)
			
			time.sleep (.1)
		
	rich.print_json (data = {
		"not found": not_found
	})	