


'''
	from prosthetic.frontiers.trends.monetary.DB_prosthetic_trends.collection_vernacular.document.insert import insert_document
	insert_document ({
		"document": {
			"domain": ""
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


'''
	FDC_ID = "",
	affiliates = [],
	goodness_certifications = []
'''
def insert_document (packet):
	document = packet ["document"]

	try:
		[ driver, DB_prosthetic_trends ] = connect_to_prosthetic_inventory ()
		collection_vernacular = DB_prosthetic_trends ["collection_vernacular"]
	except Exception as E:
		print ("food collection connect:", E)
		
	
	try:	
		essence = retrieve_essence ()
		
		inserted = collection_vernacular.insert_one (document)
		inserted_document = collection_vernacular.find_one ({"_id": inserted.inserted_id })
		
		print ()
		print ("inserted:", inserted_document )
	
	except pymongo.errors.DuplicateKeyError:
		print ("""
		
			That domain already exists
			
		""")
		
		time.sleep (1)
		exit ()
		
	except Exception as E:
		print (parse_exception.now (E))
	
		raise Exception (E)
		pass;
		
	try:
		driver.close ()
	except Exception as E:
		print (parse_exception.now (E))
		print ("food collection disconnect exception:", E)	
		
	return None;








