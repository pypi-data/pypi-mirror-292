

'''
	import prosthetic.modules.moves.mint_to_trends as mint_to_trends
	mint_to_trends.start ()
'''

import pymongo
from gridfs import GridFS
import pathlib
from os.path import dirname, join, normpath
import os

import prosthetic.essence as prosthetic_essence
from prosthetic.modules.freight.save import zip_and_save_to_gridfs

def start (
	name = ''
):
	essence_mongo = prosthetic_essence.find ("mongo")

	DB_name = essence_mongo ["DB_name"]
	DB_collection_zips = essence_mongo ["passes"] ['GridFS_zips']
	DB_collection_zips_files = essence_mongo ["passes"] ['GridFS_zips_files']
	mongo_connection = essence_mongo ["connection"]
	
	client = pymongo.MongoClient (mongo_connection)
	DB = client [ DB_name ]
	GridFS_collection = GridFS (DB, collection = DB_collection_zips)
	GridFS_collection_files = DB [ DB_collection_zips_files ]

	id = zip_and_save_to_gridfs (
		name = name,
		directory_path = str (normpath (join (os.getcwd (), name))), 
		
		metadata = None,
		
		GridFS_collection = GridFS_collection,
		GridFS_collection_files = GridFS_collection_files
	)

	DB ["passes"].insert_one ({
		"legal": {
			"name": name,
			"tags": [],
			"locks": [] 
		},
		"zip": id
	})