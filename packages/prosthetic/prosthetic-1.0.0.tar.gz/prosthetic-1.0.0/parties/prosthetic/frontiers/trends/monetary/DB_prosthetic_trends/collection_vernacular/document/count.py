




'''
	from prosthetic.frontiers.trends.monetary.DB_prosthetic_trends.collection_vernacular.document.count import count_treasures
	count_treasures ()
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



def count_treasures ():
	try:
		[ driver, DB_prosthetic_trends ] = connect_to_prosthetic_inventory ()
		collection_vernacular = DB_prosthetic_trends ["collection_vernacular"]
	except Exception as E:
		print ("food collection connect:", E)
		
	count = "unknown"
	try:	
		essence = retrieve_essence ()
		
		print ("filter:", filter)
		
		count = collection_vernacular.count_documents ({})
		
	except Exception as E:
		print (parse_exception.now (E))
	
		raise Exception (E)
		pass;
		
	try:
		driver.close ()
	except Exception as E:
		print (parse_exception.now (E))
		print ("food collection disconnect exception:", E)	
		
		
	return count;








