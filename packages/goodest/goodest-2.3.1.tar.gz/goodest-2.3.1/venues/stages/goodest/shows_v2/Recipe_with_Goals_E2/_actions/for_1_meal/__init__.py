
'''
	from goodest.shows_v2.Recipe_with_Goals_E2._actions.for_1_meal import build_recipe_with_goals_for_1_meal
	build_recipe_with_goals_for_1_meal ({
		"meal": {
			"emblem": "4"
		},
		"goal": {
			"emblem": "2"
		}
	})
'''


#\
#
import rich
#
#
from goodest.adventures.monetary.DB.goodest_tract.goals.retrieve_one import retrieve_one_goal
from goodest.adventures.monetary.DB.goodest_inventory.collect_meals.document.find import find_meal
#
#/

from goodest.shows_v2.Recipe_with_Goals_E2._actions.build import add_goals_to_essential_nutrients_grove


	
def build_recipe_with_goals_for_1_meal (packet):
	goal_emblem = packet ["goal"] ["emblem"]
	
	#\
	#	Find the food document
	#
	#
	meal_document = find_meal ({
		"filter": {
			"emblem": packet ["meal"] ["emblem"]
		}
	})
	essential_nutrients_grove = meal_document ["nature"] ["essential nutrients"] ["grove"]

	#\
	#
	add_goals_to_essential_nutrients_grove ({
		"essential_nutrients_grove": essential_nutrients_grove,
		"goals": retrieve_one_goal ({
			"emblem": goal_emblem
		}) ["nature"]
	})
	#
	#/
	
	''''
	#\
	#	Overwrite the food recipes.
	#
	#
	grocery_document ["nature"] ["essential nutrients"] = recipe_packet ["essential nutrients"]
	grocery_document ["nature"] ["cautionary ingredients"] = recipe_packet ["cautionary ingredients"]
	#
	#/
	"'''
	
	
	return meal_document
	