

'''	
	python3 status.proc.py shows_v2/Recipe_with_Goals_E2/_actions/for_1_food/_status/status_1.py
'''

from goodest.shows_v2.Recipe_with_Goals_E2._actions.for_1_grocery import build_recipe_with_goals_for_1_grocery 
from goodest.shows_v2.Recipe_with_Goals_E2._actions.build import build_recipe_with_goals
from goodest.shows_v2.treasure.nature.land.grove._ops.seek_name_or_accepts import seek_name_or_accepts
from goodest.adventures.monetary.DB.goodest_tract.goals.retrieve_one import retrieve_one_goal

import pathlib
from os.path import dirname, join, normpath
from goodest.mixes.drives.etch.bracket import etch_bracket
this_directory = pathlib.Path (__file__).parent.resolve ()


def check_dietary_fiber (essential_nutrients_grove):
	'''
		The math is not checked.
		However, the consitency against previous results is.
		
		"attained": {
			"RDA": {
				"mass + mass equivalents": {
					"per recipe": {
						"Earth days": {
							"fraction string": "227/70",
							"sci note string": "3.2429e+0"
						}
					}
				}
			}
		}
	'''
	dietary_fiber = seek_name_or_accepts (
		grove = essential_nutrients_grove,
		name_or_accepts = "dietary fiber"
	)
	dietary_RDA_Earth_days = dietary_fiber ["attained"] ["RDA"] ["mass + mass equivalents"] ["per recipe"] ["Earth days"]
	assert (
		dietary_RDA_Earth_days ["fraction string"] ==
		"227/70"
	), dietary_RDA_Earth_days
	assert (
		dietary_RDA_Earth_days ["sci note string"] ==
		"3.2429e+0"
	), dietary_fiber
	
	

def check_1 ():
	goal_emblem = 14;

	food = build_recipe_with_goals_for_1_grocery ({
		"food": {
			"emblem": 11
		},
		"goal": {
			"emblem": goal_emblem
		}
	})
	etch_bracket (normpath (join (this_directory, "status_1_food.JSON")), food)	
	
	
	recipe_packet = build_recipe_with_goals ({
		"IDs_with_amounts": [
			{
				"FDC_ID": "1795141",
				"packages": 1
			}
		],
		"goals": retrieve_one_goal ({
			"emblem": goal_emblem
		}) ["nature"]
	})
	
	check_dietary_fiber (food ["nature"] ["essential nutrients"] ["grove"])
	check_dietary_fiber (recipe_packet ["essential nutrients"] ["grove"])
	
checks = {
	'check 1': check_1
}


