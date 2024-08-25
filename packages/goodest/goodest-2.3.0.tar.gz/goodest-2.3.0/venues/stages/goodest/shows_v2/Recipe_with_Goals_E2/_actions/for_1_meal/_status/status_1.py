

'''	
	python3 status.proc.py shows_v2/Recipe_with_Goals_E2/_actions/for_1_meal/_status/status_1.py
'''

from goodest.shows_v2.treasure.nature.land.grove._ops.seek_name_or_accepts import seek_name_or_accepts
from goodest.shows_v2.Recipe_with_Goals_E2._actions.for_1_meal import build_recipe_with_goals_for_1_meal
	

import pathlib
from os.path import dirname, join, normpath
from goodest.mixes.drives.etch.bracket import etch_bracket
this_directory = pathlib.Path (__file__).parent.resolve ()


def check_grove_qualities (essential_nutrients_grove):
	'''
		The math is not checked.
		However, the consitency against previous results is.
		
		 "goal": {
			"labels": [
				"Protein"
			],
			"criteria": {
				"RDA": {
					"mass + mass equivalents": {
						"per Earth day": {
							"grams": {
								"fraction string": "50",
								"sci note string": "5.0000e+1"
							}
						}
					}
				}
			},
			"references": [
				"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
			]
		},
		"attained": {
			"RDA": {
				"mass + mass equivalents": {
					"per recipe": {
						"Earth days": {
							"fraction string": "10955006093578731/2814749767106560000",
							"sci note string": "3.8920e-3"
						}
					}
				}
			}
		}
	'''
	quality = seek_name_or_accepts (
		grove = essential_nutrients_grove,
		name_or_accepts = "protein"
	)
	
	#
	#
	#	goals
	#
	#
	quality_goal_criteria_RDA = quality ["goal"] ["criteria"] ["RDA"] ["mass + mass equivalents"] ["per Earth day"] ["grams"]
	assert (
		quality_goal_criteria_RDA ["fraction string"] ==
		"50"
	), quality_goal_criteria_RDA
	assert (
		quality_goal_criteria_RDA ["sci note string"] ==
		"5.0000e+1"
	), quality_attained_RDA_Earth_days
	
	#
	#
	#	attained RDA
	#
	#
	quality_attained_RDA_Earth_days = quality ["attained"] ["RDA"] ["mass + mass equivalents"] ["per recipe"] ["Earth days"]
	assert (
		quality_attained_RDA_Earth_days ["fraction string"] ==
		"10955006093578731/2814749767106560"
	), quality_attained_RDA_Earth_days
	assert (
		quality_attained_RDA_Earth_days ["sci note string"] ==
		"3.8920e+0"
	), quality_attained_RDA_Earth_days
	
	
	
	

def check_1 ():
	goal_emblem = "14"

	meal = build_recipe_with_goals_for_1_meal ({
		"meal": {
			"emblem": 1
		},
		"goal": {
			"emblem": goal_emblem
		}
	})
	etch_bracket (normpath (join (this_directory, "meal.JSON")), meal)	
	
	essential_nutrients_grove = meal ["nature"] ["essential nutrients"] ["grove"]
	check_grove_qualities (essential_nutrients_grove)
	
	
	
	
checks = {
	'check 1': check_1
}




