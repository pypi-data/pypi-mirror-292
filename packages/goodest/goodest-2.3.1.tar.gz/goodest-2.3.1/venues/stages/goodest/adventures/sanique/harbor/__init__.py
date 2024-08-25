



'''
	https://sanic.dev/en/guide/running/manager.html#dynamic-applications

	worker manager:
		https://sanic.dev/en/guide/running/manager.html

	Asynchronous Server Gateway Interface, ASGI:
		https://sanic.dev/en/guide/running/running.html#asgi
		
		uvicorn harbor:create
		
	Robyn, rust
		https://robyn.tech/
		
	https://sanic.dev/en/plugins/sanic-ext/openapi/decorators.html#ui
'''


#\
#
import json
import os
import traceback
#
#
import sanic
from sanic import Sanic
from sanic_ext import openapi, Extend
#from sanic_openapi import swagger_blueprint, openapi_metadata
#from sanic_openapi import swagger_blueprint, doc
import sanic.response as sanic_response
#
#
from goodest.mixes.show.variable import show_variable
#
#
from goodest._essence import retrieve_essence, build_essence
#
#
from .sockets_guests 				import sockets_guests
#
from .hype_guests._addresses 		import hype_guest_addresses
from .hype_guests.bits 				import hype_guest_bits
from .hype_guests.front				import hype_guests_front
from .hype_guests.inventory.foods 	import hype_guest_foods
from .hype_guests.inventory.supps 	import hype_guest_supps
from .hype_guests.inventory.recipes	import hype_guest_recipes
#
#
from .hype_technicians.Quests				import hype_technicians_Quests
from .hype_technicians._addresses			import hype_technicians_addresses
from .hype_technicians.friends.USDA_food 	import hype_technicians_USDA_food
from .hype_technicians.friends.NIH_supp 	import hype_technicians_NIH_supp
from .hype_technicians.inventory			import hype_technicians_inventory
#
#/

'''
	https://sanic.dev/en/guide/running/running.html#using-a-factory
'''
def create ():
	inspector_port = os.environ.get ('inspector_port')
	env_vars = os.environ.copy ()
	
	
	build_essence (env_vars ["essence_path"])
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
	
	#
	#
	#	https://sanic.dev/en/plugins/sanic-ext/openapi/basics.html#changing-specification-metadata
	#
	app.ext.openapi.describe(
		"API.RPC",
		version = "0.0.0",
		description = ("""
		
		Outline:
		
			Most of these moves are or should be, at the very least either,
				
				"[patch] /guests"
				"[patch] /technicians"
				
				"patch" is utilized because it accepts JSON.
				
				Normal HTTP verb rules aren't utilized.
				
				The goal is to use websockets instead of patches.
				
					modify {}
					insert {}
					remove {}
					find {}
		
		Map:
			Guests:
				Front: 			[get] /
			
				Search: 		[patch] /guests
			
				Find Food:		[patch] /guests
				Find Supp:		[patch] /guests
				Find Meal:		[patch] /guests
				
				Find Goal:		
				Find Goals:		[patch] /guests
				
				Find Recipe:	[patch] /guests		
			
			Technicians:
				Add Food:
				Add Supp:
				Add Meal:
				
				Add Goal:
				
				
				Friends:
					"These make external API calls to USDA or NIH".
				
					USDA Food:
					
					NIH Supp:
					
					
						
						
		""")
	)
	
	#app.blueprint (swagger_blueprint)
	app.config.INSPECTOR = True
	app.config.INSPECTOR_HOST = "0.0.0.0"
	app.config.INSPECTOR_PORT = int (inspector_port)
	

	if (essence ["mode"] == "nurture"):
		#
		#	https://sanic.dev/en/plugins/sanic-ext/http/cors.html#configuration
		#
		#
		@app.middleware ('response')
		async def before_route_middleware (request, response):
			URL = request.url
			response.headers['Access-Control-Allow-Origin'] = '*'
			response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
			response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
			response.headers['Access-Control-Allow-Credentials'] = 'true'
			
			print ('Middleware before every route "response":', URL)
			
			return;

	
	#
	#	opener
	#
	#
	#app.ext.openapi.add_security_scheme ("api_key", "apiKey")
	app.ext.openapi.add_security_scheme ("api_key", "http")
	

	#\
	# 
	#	Guests 
	#
	hype_guests_front ({
		"app": app
	})
	#
	hype_guest_addresses ({
		"app": app
	})
	#
	hype_guest_bits ({
		"app": app,
	})
	#
	hype_guest_recipes ({
		"app": app
	})
	hype_guest_foods ({
		"app": app
	})
	hype_guest_supps ({
		"app": app
	})
	#
	#
	sockets_guests ({
		"app": app
	})
	# 
	#/
	

	#\
	#
	#	Technicians
	#
	hype_technicians_Quests ({ "app": app })
	#
	hype_technicians_addresses ({ "app": app })
	#
	hype_technicians_USDA_food ({
		"app": app,
		"openapi": openapi
	})
	hype_technicians_NIH_supp ({
		"app": app,
		"openapi": openapi
	})
	#
	hype_technicians_inventory ({ "app": app })
	#
	#/
	

	return app

