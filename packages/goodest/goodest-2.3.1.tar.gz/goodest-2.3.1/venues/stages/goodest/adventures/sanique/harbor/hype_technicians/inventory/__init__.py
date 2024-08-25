


#\
#
from .foods 	import hype_technicians_inventory_foods
from .recipes 	import hype_technicians_inventory_recipes
from .supps 	import hype_technicians_inventory_supps
#
#
from goodest._essence import retrieve_essence, build_essence
from goodest.adventures.sanique.utilities.check_key import check_key
from goodest.adventures.monetary.DB.goodest_inventory.foods.document.insert import insert_food	
#
#
import sanic
from sanic import Sanic
from sanic_ext import openapi
import sanic.response as sanic_response
#
#/

def hype_technicians_inventory (packet):
	app = packet ["app"]

	inventory_blueprint = sanic.Blueprint (
		"Technicians_Inventory", 
		url_prefix = "/Technicians/Inventory"
	)

	hype_technicians_inventory_foods ({
		"blue_print": inventory_blueprint
	})
	hype_technicians_inventory_supps ({
		"blue_print": inventory_blueprint
	})
	hype_technicians_inventory_recipes ({
		"blue_print": inventory_blueprint
	})
		
	app.blueprint (inventory_blueprint)