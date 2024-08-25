
'''
	from goodest.shows_v2.Recipe_with_Goals_E2._actions.for_1_grocery import build_recipe_with_goals_for_1_grocery 
	build_recipe_with_goals_for_1_grocery ({
		"food": {
			"emblem": "4"
		},
		"goal": {
			"emblem": "2"
		}
	})
'''

''''
	from goodest.shows_v2.Recipe_with_Goals_E2._actions.for_1_grocery import build_recipe_with_goals_for_1_grocery 
	build_recipe_with_goals_for_1_grocery ({
		"supp": {
			"emblem": "4"
		},
		"goal": {
			"emblem": "2"
		}
	})
"'''

#\
#
import rich
#
#
from goodest.adventures.monetary.DB.goodest_tract.goals.retrieve_one import retrieve_one_goal
#
from goodest.adventures.monetary.DB.goodest_inventory.foods.document.find import find_food
from goodest.adventures.monetary.DB.goodest_inventory.supps.document.find import find_supp
from goodest.adventures.monetary.DB.goodest_inventory.collect_meals.document.find import find_meal
#
#
from goodest.shows_v2.Recipe_with_Goals_E2._actions.build import build_recipe_with_goals
#
#/
	
def build_recipe_with_goals_for_1_grocery (packet):
	goal_emblem = packet ["goal"] ["emblem"]
	
	
	IDs_with_amounts = []
	
	#\
	#	Find the food document
	#
	#
	if ("food" in packet):
		grocery_document = find_food ({
			"filter": {
				"emblem": packet ["food"] ["emblem"]
			}
		})
		FDC_ID = grocery_document ["nature"] ["identity"] ["FDC ID"]
		IDs_with_amounts.append ({
			"FDC_ID": FDC_ID,
			"packages": 1
		})
		
	elif ("supp" in packet):
		grocery_document = find_supp ({
			"filter": {
				"emblem": packet ["supp"] ["emblem"]
			}
		})
		DSLD_ID = grocery_document ["nature"] ["identity"] ["DSLD ID"]
		IDs_with_amounts.append ({
			"DSLD_ID": DSLD_ID,
			"packages": 1
		})		
	else:
		raise Exception ('"food", "supp", or "meal" was not found in the packet.')
	#
	#/
	
	#\
	#	Build the recipe with goals
	#
	#
	recipe_packet = build_recipe_with_goals ({
		"IDs_with_amounts": IDs_with_amounts,
		"goals": retrieve_one_goal ({
			"emblem": goal_emblem
		}) ["nature"]
	})
	#/
	
	#\
	#	Overwrite the food recipes.
	#
	#
	grocery_document ["nature"] ["essential nutrients"] = recipe_packet ["essential nutrients"]
	grocery_document ["nature"] ["cautionary ingredients"] = recipe_packet ["cautionary ingredients"]
	#
	#/
	
	return grocery_document
	