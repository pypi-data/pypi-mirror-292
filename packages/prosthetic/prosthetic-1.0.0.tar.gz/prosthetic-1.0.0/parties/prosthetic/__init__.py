
#/
#
from prosthetic._clique import clique
from prosthetic.frontiers.trends.monetary.DB_prosthetic_trends.collection_vernacular._indexes import prepare_collection_vernacular_indexes
#
#
import rich
#
#
import pathlib
import inspect
import os
from os.path import dirname, join, normpath
#
#\

# prepare_collection_vernacular_indexes ()

configured = False


def is_configured ():
	return configured

def start ():

	return;

	prosthetic_config = config_scan.start ()
	if (prosthetic_config == False): 
		#print ("prosthetic_config == False")
		
		print ("The config was not found; exiting.")
		print ()
		
		exit ();
		
		return;

	print ()
	print ("configuring")
	print ()
	
	print ('merging config', prosthetic_config)
	prosthetic_essence.merge_config (prosthetic_config ["configuration"])
	
	
	rich.print_json (data = prosthetic_essence.essence)
	rich.print_json (data = prosthetic_essence.essence)
	
	
	return;


	'''
	rich.print_json (data = {
		"prosthetic_config": prosthetic_config
	})
	'''
	
	'''
	prosthetic_essence.change ("mongo", {
		"directory": ""
	})
	'''
	
	'''
		get the absolute paths
	'''
	'''
	prosthetic_config ["configuration"] ["treasuries"] ["path"] = (
		normpath (join (
			prosthetic_config ["directory_path"], 
			prosthetic_config ["configuration"] ["treasuries"] ["path"]
		))
	)
	'''
	
	
	'''
		paths:
			trends
				mongo_data_1
	
	
		mongo:
			safety
				passes
				zips
				zips.files
	'''
	trends_path = normpath (join (
		prosthetic_config ["directory_path"], 
		prosthetic_config ["configuration"] ["trends"] ["path"]
	))
	edited_config = {
		"mints": {
			"path": normpath (join (
				prosthetic_config ["directory_path"], 
				prosthetic_config ["configuration"] ["mints"] ["path"]
			))
		},
		"trends": {
			"path": trends_path,
			
			"nodes": [{
				"host": "localhost",
				"port": "27017",
				"data path": normpath (join (
					trends_path, 
					"mongo_data_1"
				))
			}]
		},
		"CWD": prosthetic_config ["directory_path"]
	}
	
	'''
	config_template = {
		
	}
	'''
	
	rich.print_json (data = {
		"edited_config": edited_config
	})

	
	prosthetic_essence.change ("edited_config", edited_config)
	

	#print ('prosthetic configuration', prosthetic_config.configuration)

	'''
		Add the changed version of the basal config
		to the essence.
	'''
	'''
	config = prosthetic_config ["configuration"];
	for field in config: 
		prosthetic_essence.change (field, config [field])
	'''
	
	configured = True
	
	print ()
