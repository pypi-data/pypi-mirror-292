


''''
	from prosthetic.frontiers.trends.monetary.DB_prosthetic_trends.connect import connect_to_prosthetic_inventory
	[ driver, prosthetic_inventory_DB ] = connect_to_prosthetic_inventory ()
	collection_vernacular = DB_prosthetic_trends ["collection_vernacular"]
	driver.close ()
"'''



#/
#
from prosthetic.frontiers.trends.monetary.moves.URL.retrieve import retreive_monetary_URL
from prosthetic._essence import retrieve_essence
#
#
import pymongo
#
#\

def connect_to_prosthetic_inventory ():
	essence = retrieve_essence ()
	
	ingredients_DB_name = essence ["trends"] ["monetary"] ["databases"] ["DB_prosthetic_trends"] ["alias"]
	monetary_URL = retreive_monetary_URL ()

	driver = pymongo.MongoClient (monetary_URL)

	return [
		driver,
		driver [ ingredients_DB_name ]
	]