



'''	
	python3 status.proc.py shows_v2/Recipe_with_Goals_E2/_actions/for_1_grocery/_status_supp/status_1.py
'''

from goodest.shows_v2.Recipe_with_Goals_E2._actions.for_1_grocery import build_recipe_with_goals_for_1_grocery
from goodest.shows_v2.Recipe_with_Goals_E2._actions.build import build_recipe_with_goals
from goodest.shows_v2.treasure.nature.land.grove._ops.seek_name_or_accepts import seek_name_or_accepts
from goodest.adventures.monetary.DB.goodest_tract.goals.retrieve_one import retrieve_one_goal

import pathlib
from os.path import dirname, join, normpath
from goodest.mixes.drives.etch.bracket import etch_bracket
this_directory = pathlib.Path (__file__).parent.resolve ()


def check_qualities (essential_nutrients_grove):
	'''
		The math is not checked.
		However, the consitency against previous results is.
		
		"attained": {
			"RDA": {
				"mass + mass equivalents": {
					"per recipe": {
						"Earth days": {
							"fraction string": "90/13",
							"sci note string": "6.9231e+0"
						}
					}
				}
			}
		}
	'''
	quality = seek_name_or_accepts (
		grove = essential_nutrients_grove,
		name_or_accepts = "calcium"
	)
	quality_Earth_days = quality ["attained"] ["RDA"] ["mass + mass equivalents"] ["per recipe"] ["Earth days"]
	assert (
		quality_Earth_days ["fraction string"] ==
		"90/13"
	), quality_Earth_days
	assert (
		quality_Earth_days ["sci note string"] ==
		"6.9231e+0"
	), quality_Earth_days
	
	
#
#
#	{ "nature.identity.DSLD ID": "276336" }
#
#
def check_1 ():
	supp_emblem = 2
	supp_DSLD_ID = "276336"
	goal_emblem = "14"

	supp = build_recipe_with_goals_for_1_grocery ({
		"supp": {
			"emblem": supp_emblem
		},
		"goal": {
			"emblem": goal_emblem
		}
	})
	etch_bracket (normpath (join (this_directory, "status_1_supp.JSON")), supp)	
	
	
	#
	#
	#	This is the equality check build.
	#
	#
	recipe_packet = build_recipe_with_goals ({
		"IDs_with_amounts": [
			{
				"DSLD_ID": supp_DSLD_ID,
				"packages": 1
			}
		],
		"goals": retrieve_one_goal ({
			"emblem": goal_emblem
		}) ["nature"]
	})
	
	check_qualities (supp ["nature"] ["essential nutrients"] ["grove"])
	check_qualities (recipe_packet ["essential nutrients"] ["grove"])
	
checks = {
	'check 1': check_1
}


