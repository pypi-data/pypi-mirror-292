



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
#
from .quests.insert_meal import insert_meal_quest
from .checks import quest_questionaire
#
#/



decription = """

	{
		"label": "insert meal",
		"freight": {
			"name": "rice and beans",
			"formulate": {
				"IDs_with_amounts": [
					{
						"FDC_ID": "2471166",
						"grams": 1
					},
					{
						"FDC_ID": "2425001",
						"grams": 2
					}
				]
			}
		}
	}
	

"""

quests = {
	"insert meal": insert_meal_quest
}

def hype_technicians_Quests (packet):
	app = packet ["app"]

	Technicians_addresses = sanic.Blueprint ("Technicians_Quests", url_prefix = "/Technicians/Quests")
	
	
	@Technicians_addresses.route ("/", methods = [ "patch" ])
	@openapi.parameter ("opener", str, "header")
	@openapi.description (decription)
	@openapi.body ({
		"application/json": {
			"properties": {
				"label": { "type": "string" },
				"freight": { "type": "object" }
			}
		}
	})
	async def Technicians_patches (request):
		lock_status = check_key (request)
		if (lock_status != "unlocked"):
			return lock_status
	
		essence = retrieve_essence ()
		
		questionaire_revenue = quest_questionaire (request, quests)
		if ("problem" in questionaire_revenue):
			return sanic.json (questionaire_revenue ["problem"])	
		
		the_ask = questionaire_revenue ["the_ask"]
		the_ask_label = the_ask ["label"]
		the_ask_freight = the_ask ["freight"]
		
		try:
			proceeds = quests [ the_ask_label ] ({
				"freight": the_ask_freight
			})
		except Exception as E:
			return sanic.json ({
				"label": "unfinished",
				"freight": {
					"description": "An exception occurred while generating the proceeds.",
					"label": the_ask_label,
					"exception": parse_exception.now (E)
				}
			})	
			
		return sanic.json (proceeds, status = 200)
		

	app.blueprint (Technicians_addresses)
