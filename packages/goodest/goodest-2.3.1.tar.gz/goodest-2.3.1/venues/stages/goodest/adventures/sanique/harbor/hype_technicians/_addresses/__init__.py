



#\
#
import sanic
from sanic import Sanic
from sanic_ext import openapi
import sanic.response as sanic_response
#
#
import law_dictionary
import ships.modules.exceptions.parse as parse_exception
#
#
from goodest._essence import retrieve_essence, build_essence
from goodest.adventures.sanique.utilities.check_key import check_key
#
from goodest.shows_v2.recipe._ops.retrieve import retrieve_recipe
#
#/

def hype_technicians_addresses (packet):
	app = packet ["app"]

	Technicians_addresses = sanic.Blueprint ("Technicians", url_prefix = "/Technicians")
	
	
	@Technicians_addresses.route ("/essence")
	@openapi.parameter ("opener", str, "header")
	async def address_essence (request):
		lock_status = check_key (request)
		if (lock_status != "unlocked"):
			return lock_status
	
		essence = retrieve_essence ()
		return sanic.json (essence)
		
		
	@Technicians_addresses.get ('/goals/<region>')
	@openapi.summary ("goals")
	@openapi.description ("goals")
	@openapi.parameter ("opener", str, "header")
	async def goals_by_region (request, region):
		lock_status = check_key (request)
		if (lock_status != "unlocked"):
			return lock_status
	
		try:
			ingredient_doc = retrieve_one_goal ({
				"region": region
			})
			
			return sanic_response.json (ingredient_doc)
			
		except Exception as E:
			show_variable (str (E))
			
		return sanic_response.json ({
			"anomaly": "An unaccounted for anomaly occurred."
		}, status = 600)
		
	
	app.blueprint (Technicians_addresses)
	
	

