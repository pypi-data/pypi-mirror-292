

#----
#
import pathlib
from os.path import dirname, join, normpath
import sys
import os
#
#
import pydash
#
#----

def establish_alerts_allowed (alert_level):
	alert_ranks = [ "scholar", "info", "caution", "emergency", "front" ]

	alert_found = False;
	allow_alerts = []
	for alert_rank in alert_ranks:
		if (alert_level == alert_rank):
			alert_found = True;
			
		# print ("alert_rank:", alert_rank, alert_level, alert_level == alert_rank)			
			
		if (alert_found):
			allow_alerts.append (alert_rank)
			
	# print ("allow_alerts:", allow_alerts)		
	
	return allow_alerts

def merge_essence (
	prefab_essence, 
	external_essence
):
	this_directory = pathlib.Path (__file__).parent.resolve ()	
	the_mix_directory = str (normpath (join (this_directory, "../..")));

	'''
		"onsite": {
			"host": "0.0.0.0",
			"port": "39000",
			
			"path": crate ("monetary_1/data"),
			"logs_path": crate ("monetary_1/logs/the.logs"),
			"PID_path": crate ("monetary_1/the.process_identity_number"),
		}
	'''
	the_merged_essence = pydash.merge (
		prefab_essence,
		external_essence
	)
	
	
	
	the_merged_essence ["allowed_alerts"] = establish_alerts_allowed (
		the_merged_essence ["alert_level"]
	)
	
	#print ("allowed alerts", the_merged_essence ["allowed_alerts"])

	
	return the_merged_essence