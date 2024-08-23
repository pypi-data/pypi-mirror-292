

'''
	itinerary:
		[ ] pass the current python path to this procedure
'''


'''
	https://sanic.dev/en/guide/running/manager.html#dynamic-applications
'''

'''
	worker manager:
		https://sanic.dev/en/guide/running/manager.html
'''

'''
	Asynchronous Server Gateway Interface, ASGI:
		https://sanic.dev/en/guide/running/running.html#asgi
		
		uvicorn harbor:create
'''

'''
	Robyn, rust
		https://robyn.tech/
'''

'''
	--factory
'''

#/
#
#
from .guest_sockets import sockets_guest
#
from .guest_regions import guest_regions
#
from prosthetic.frontiers.trends.sanique.utilities.generate_inventory_paths import generate_inventory_paths
#
from prosthetic._essence import retrieve_essence, build_essence
from prosthetic.frontiers.trends.alerting import activate_alert
from prosthetic.frontiers.trends.alerting.parse_exception import parse_exception
#
#
import sanic
from sanic import Sanic
from sanic_ext import openapi, Extend
import sanic.response as sanic_response
import rich
#
#
import json
import os
import traceback
#
#\_

'''
	https://sanic.dev/en/guide/running/running.html#using-a-factory
'''
def create (* positionals):
	print ("positionals", positionals)

	inspector_port = os.environ.get ('inspector_port')
	env_vars = os.environ.copy ()
	
	essence_path = env_vars ['essence_path']
	
	rich.print_json (data = {
		"env_vars": env_vars
	})
	

	
	build_essence ({
		"path": essence_path
	})
	
	essence = retrieve_essence ()
	
	
	'''
		#
		#	https://sanic.dev/en/guide/running/configuration.html#inspector
		#
		INSPECTOR_PORT
	'''
	
	app = Sanic (__name__)
	
	app.extend (config = {
		"oas_url_prefix": "/docs",
		"swagger_ui_configuration": {
			"docExpansion": "list" # "none"
		},
	})
	
	#app.blueprint (swagger_blueprint)
	app.config.INSPECTOR = True
	app.config.INSPECTOR_HOST = "0.0.0.0"
	app.config.INSPECTOR_PORT = int (inspector_port)
	
	
	
	#
	#	https://sanic.dev/en/plugins/sanic-ext/http/cors.html#configuration
	#
	#
	@app.middleware ('response')
	async def before_route_middleware (request, response):
		URL = request.url
		response.headers['Access-Control-Allow-Origin'] = '*'
		response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
		response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
		response.headers['Access-Control-Allow-Credentials'] = 'true'
		
		print ('Middleware before every route "response":', URL)
		#print ('headers', response.headers)
	
	#
	#	opener
	#
	#
	#app.ext.openapi.add_security_scheme ("api_key", "apiKey")
	app.ext.openapi.add_security_scheme ("api_key", "http")
	
	
	guest_regions ({
		"app": app
	})
	
	
	

		
	return app

