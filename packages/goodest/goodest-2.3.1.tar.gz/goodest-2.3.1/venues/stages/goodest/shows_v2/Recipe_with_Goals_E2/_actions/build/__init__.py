

''''
	from goodest.shows_v2.Recipe_with_Goals_E2._actions.build import build_recipe_with_goals
	from goodest.adventures.monetary.DB.goodest_tract.goals.retrieve_one import retrieve_one_goal
	recipe_packet = build_recipe_with_goals ({
		"IDs_with_amounts": [
			{
				"FDC_ID": "2677998",
				"packages": 1
			}
		],
		"goals": retrieve_one_goal ({
			"emblem": "12"
		}) ["nature"]
	})
"'''

''''
	from goodest.shows_v2.Recipe_with_Goals_E2._actions.build import add_goals_to_essential_nutrients_grove
	from goodest.adventures.monetary.DB.goodest_tract.goals.retrieve_one import retrieve_one_goal
	recipe_packet = add_goals_to_essential_nutrients_grove ({
		"essential_nutrients_grove": [],
		"goals": retrieve_one_goal ({
			"emblem": "12"
		}) ["nature"]
	})
"'''

''''
proceeds: {
	"essential nutrients": {},
	"cautionary ingredients": {}
}
"'''


#\
#
from goodest.shows_v2.recipe._ops.retrieve import retrieve_recipe
#
#
from .procedures.add_goals import add_goals
#
#/


def add_goals_to_essential_nutrients_grove (packet):
	essential_nutrients_grove = packet ["essential_nutrients_grove"]
	goals = packet ["goals"]
	
	''' 
		TODO:
			This adds the goals to the essential_nutrients grove 
			of the recipe.
	'''
	add_goals ({
		"essential_nutrients_grove": essential_nutrients_grove,
		"goals": goals,
		"records": 1
	})
	


def build_recipe_with_goals (packet):
	IDs_with_amounts = packet ["IDs_with_amounts"]
	goals = packet ["goals"]
	
	''''
		TODO:
			Build the recipe packet.
	"'''
	recipe_packet = retrieve_recipe ({
		"location": "mongo",
		"IDs_with_amounts": IDs_with_amounts
	})
	recipe = recipe_packet ["recipe"]
	essential_nutrients_grove = recipe ["essential nutrients"] ["grove"]
	
	
	''' 
		TODO:
			This adds the goals to the essential_nutrients grove 
			of the recipe.
	'''
	add_goals ({
		"essential_nutrients_grove": essential_nutrients_grove,
		"goals": goals,
		"records": 1
	})
	
	return recipe