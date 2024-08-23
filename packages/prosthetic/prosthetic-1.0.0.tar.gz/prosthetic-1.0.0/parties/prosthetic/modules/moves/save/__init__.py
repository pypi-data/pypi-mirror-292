
'''
	itinerary:
		steps:
			

'''


'''
	import prosthetic.modules.moves.save as save
	save.save ()
'''

import pymongo
from gridfs import GridFS
import pathlib
from os.path import dirname, join, normpath
import os

from prosthetic._essence import retrieve_essence
from .modules.zip_and_save_to_gridfs import zip_and_save_to_gridfs

def save (
	name = ''
):
	edited_config = essence.find ("edited_config")

	id = zip_and_save_to_gridfs (
		name = name,
		directory_path = str (normpath (join (edited_config ["mints"] ["path"], name))), 
		
		metadata = None
	)

	proceeds = essence.link ().insert_one ({
		"legal": {
			"name": name,
			"tags": [],
			"locks": [] 
		},
		"zip": id
	})
	print ("added pass _id:", proceeds.inserted_id)
	
	'''
		Figure out is inserted.
	'''
	found = essence.link ().find_one({ "_id": proceeds.inserted_id })
	assert (
		str (found ["_id"]) == str (proceeds.inserted_id)
	), [ str (found ["_id"]), str (proceeds.inserted_id)]
	
