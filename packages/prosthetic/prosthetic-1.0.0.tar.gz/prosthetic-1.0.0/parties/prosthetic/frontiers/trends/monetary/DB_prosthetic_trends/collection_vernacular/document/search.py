




'''
	from prosthetic.frontiers.trends.monetary.DB_prosthetic_trends.collection_vernacular.document.search import search_trends_vernacular
	search_trends_vernacular ({
		"filter": {
			"nature.identity.FDC ID": ""
		}
	})
'''



#/
#
from prosthetic._essence import retrieve_essence
from prosthetic.frontiers.trends.monetary.DB_prosthetic_trends.connect import connect_to_prosthetic_inventory
#
#
import ships.modules.exceptions.parse as parse_exception
#
#
import pymongo
#
#
import time
#
#\



def search_trends_vernacular (packet):
	filter = packet ["filter"]

	try:
		[ driver, DB_prosthetic_trends ] = connect_to_prosthetic_inventory ()
		collection_vernacular = DB_prosthetic_trends ["collection_vernacular"]
	except Exception as E:
		print ("collection_vernacular connect exception:", E)
		
	treasures_roster = []
	try:	
		essence = retrieve_essence ()
		
		print ("filter:", filter)
		
		treasures_roster = []
		treasures = collection_vernacular.find (filter)
		for treasure in treasures:
			treasure ["_id"] = str (treasure ["_id"]) 
			
			treasures_roster.append (treasure)
		
	except Exception as E:
		print (parse_exception.now (E))
	
		raise Exception (E)
		pass;
		
	try:
		driver.close ()
	except Exception as E:
		print (parse_exception.now (E))
		print ("food collection disconnect exception:", E)	
		
		
	return treasures_roster;








