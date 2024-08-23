



#/
#
from prosthetic._essence import retrieve_essence
from prosthetic.frontiers.trends.sanique.utilities.generate_inventory_paths import generate_inventory_paths
#
#
import sanic
from sanic import Sanic
from sanic_ext import openapi
import sanic.response as sanic_response
from sanic_limiter import Limiter, get_remote_address
#
#
import json
from os.path import exists, dirname, normpath, join
from urllib.parse import unquote
import threading
import time
from fractions import Fraction
#
#\

#/
#
#	mongo
#
#
from prosthetic.frontiers.trends.monetary.DB_prosthetic_trends.collection_vernacular.document.search import search_trends_vernacular
#
#\


def guest_regions (vue_regions_packet):
	essence = retrieve_essence ()
	
	
	##/
	build_path = essence ["sveltnetics"] ["build_path"];
	the_index = build_path + "/index.html"
	the_assets = build_path + "/assets"
	
	front_inventory_paths = generate_inventory_paths (build_path)
	for front_path in front_inventory_paths:
		print ("front_path:", front_path)
		pass;
	##\
		
	
	app = vue_regions_packet ["app"]
	
	guest_addresses = sanic.Blueprint ("guest", url_prefix = "/")
	app.blueprint (guest_addresses)

	@guest_addresses.route ("/monetary/trends/itemize")
	async def monetary_trends_itemize (request):
		# cookies = request.cookies;
		trends_vernacular = search_trends_vernacular ({
			"filter": {}
		})
		
		return sanic_response.json ({
			"trends": trends_vernacular
		}, status = 200)
	
	
	@guest_addresses.route ("/")
	async def home (request):
		# cookies = request.cookies;
		
		return await sanic_response.file (the_index)
		

	@guest_addresses.route ("/<path:path>")
	async def assets_route (request, path):
		the_path = False
		
		print ()
		print ("path:", the_path)
		
		try:
			the_path = f"{ path }"
			print ("the_path:", the_path)
			
			if (the_path in front_inventory_paths):
				content_type = front_inventory_paths [ the_path ] ["mime"]
				content = front_inventory_paths [ the_path ] ["content"]
				
				print ('found:', the_path)
				print ('content_type:', content_type)
				
				return sanic_response.raw (
					content, 
					content_type = content_type,
					headers = {
						"Custom-Header-1": "custom",
						"Cache-Control": "private, max-age=31536000",
						#"Expires": "0"
					}
				)
				
		except Exception as E:
			print ("E:", E)
		
			return sanic_response.json ({
				"note": "An anomaly occurred while processing.",
				"the_path": the_path
			}, status = 600)
			
		return await sanic_response.file (the_index)


	