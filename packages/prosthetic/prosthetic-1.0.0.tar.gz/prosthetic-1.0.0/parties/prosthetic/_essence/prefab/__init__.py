

#/
#
import pathlib
from os.path import dirname, join, normpath
import os
import sys
#
#\

this_directory = pathlib.Path (__file__).parent.resolve ()	
the_mix_directory = str (normpath (join (this_directory, "../..")));
the_prosthetic_process = str (normpath (join (this_directory, "../__bin/prosthetic_1")))


def retrieve_prefab (packet):
	essence_path = packet ["essence_path"]
	essence_directory = str (os.path.dirname (essence_path))
	mints_directory = str (normpath (join (essence_directory, "mints")));
	trends_directory = str (normpath (join (essence_directory, "trends")));
	treasures_directory = str (normpath (join (essence_directory, "treasures")));
	

	CWD = os.getcwd ();

	return {
		"essence_path": essence_path,
		"essence_directory": essence_directory,
		"CWD": os.getcwd (),
		
		#
		#	summary in goodest.mixes.activate_alert
		#
		"alert_level": "caution",
		
		#
		#	modes: [ "nurture", "business" ]
		#
		"mode": "business",
		
		"the_show": the_prosthetic_process,
	
		"sanique": {
			"directory": str (normpath (join (
				the_mix_directory, 
				"frontiers/trends/sanique"
			))),
			
			"port": "22000",
			"host": "0.0.0.0",
			
			#
			#	don't modify these currently
			#
			#	These are used for retrieval, but no for launching the
			#	sanic inspector.
			#
			#	https://sanic.dev/en/guide/running/inspector.md#inspector
			#
			"inspector": {
				"port": "22001",
				"host": "0.0.0.0"
			}
		},
		
		"sveltnetics": {
			"build_path": str (normpath (join (
				the_mix_directory, 
				"frontiers/trends/sveltenetics/build"
			)))
		},

	
		"ventures": {
			"path": str (normpath (join (this_directory, "ventures_map.JSON")))
		},
		"mints": {
			"path": mints_directory
		},
		"treasures": {
			"path": treasures_directory
		},
		
		
	
		#
		#	trends
		#		node_1
		#			mongo_data
		#			mongod.pid
		#			logs.log
		#
		#	DB:safety
		#		ion:passes
		#		ion:zips
		#		ion:zips.files
		#
		"trends": {
			"path": trends_directory,
			
			"emphemeral": {
				"path": str (normpath (join (trends_directory, "[emphemeral]"))),
			},
			
			"monetary": {
				"URL": "mongodb://0.0.0.0:39000/",
				
				"node": {
					"local": "yes",
					
					"path": str (normpath (join (
						trends_directory, 
						"@monetary"
					))),
					"data_path": str (normpath (join (
						trends_directory, 
						"@monetary/data"
					))),
					"logs_path": str (normpath (join (
						trends_directory, 
						"@monetary/logs/the.logs"
					))),
					"PID_path": str (normpath (join (
						trends_directory, 
						"@monetary/the.process_identity_number"
					))),
					
					"host": "0.0.0.0",
					"port": "39000"
				},
				
				"ephemeral": str (normpath (join (
					trends_directory, 
					"@ephermeral"
				))),
				
				"databases": {
					"DB_prosthetic_trends": {
						"alias": "prosthetic_trends",
						"collections": [
							"collection_vernacular",
							
							#
							#	GridFS
							#
							#
							"collection_bits",
							"collection_bits.files"
						],
					}
				},
				"saves": {
					"path": str (normpath (join (
						trends_directory, 
						"@monetary_saves"
					))),
					"exports": {
						"databases": {
							"DB_prosthetic_trends": {
								"alias": "prosthetic_trends",
								"collections": [
									"collection_vernacular",
								]
							}
						},
						"path": str (normpath (join (
							trends_directory, 
							"@monetary_saves/exports"
						)))						
					},
					"dumps": {
						"path": str (normpath (join (
							trends_directory, 
							"@monetary_saves/dumps"
						)))
					}					
				}
			}
		},

		"glossary": {
			"path": str (normpath (join (the_mix_directory, "____glossary"))),
			"prosthetic": str (normpath (join (the_mix_directory, "____glossary/prosthetic_1"))),
		}
	}