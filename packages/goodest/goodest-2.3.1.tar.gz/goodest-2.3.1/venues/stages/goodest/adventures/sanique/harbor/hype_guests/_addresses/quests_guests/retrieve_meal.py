


#/
#
import law_dictionary
#
#
from goodest.adventures.monetary.DB.goodest_inventory.collect_meals.document.find import find_meal
from goodest.shows_v2.Recipe_with_Goals_E2._actions.for_1_meal import build_recipe_with_goals_for_1_meal
#
#\

def retrieve_meal_quest (packet):

	freight = packet ["freight"]
	
	report_freight = law_dictionary.check (
		return_obstacle_if_not_legit = True,
		allow_extra_fields = True,
		laws = {
			"filters": {
				"required": True,
				"type": dict
			}
		},
		dictionary = freight 
	)
	if (report_freight ["advance"] != True):
		return {
			"label": "unfinished",
			"freight": {
				"obstacle": report_freight,
				"obstacle number": 2
			}
		}
	filters = freight ["filters"]
	goal = freight ["goal"]
	
	
	report_filters = law_dictionary.check (
		return_obstacle_if_not_legit = True,
		allow_extra_fields = True,
		laws = {
			"emblem": {
				"required": True,
				"type": str
			}
		},
		dictionary = filters 
	)
	if (report_filters ["advance"] != True):
		return {
			"label": "unfinished",
			"freight": {
				"obstacle": report_filters,
				"obstacle number": 3
			}
		}
	

	try:
		if ("emblem" in filters):
			filters ["emblem"] = int (filters ["emblem"])
	except Exception:	
		return {
			"label": "unfinished",
			"freight": {
				"description": "The emblem couldn't be converted to an integer.",
				"obstacle number": 4
			}
		}
	
	


	#
	#
	#	This is where the meal is retrieved.
	#
	#
	le_meal = {}
	if (type (goal) == int):
		le_meal = build_recipe_with_goals_for_1_meal ({
			"meal": {
				"emblem": filters ["emblem"]
			},
			"goal": {
				"emblem": goal
			}
		})
		
		
	else:
		le_meal = find_meal ({
			"filter": {
				"emblem": filters ["emblem"]
			}
		})
	
	
	return {
		"label": "finished",
		"freight": le_meal
	}