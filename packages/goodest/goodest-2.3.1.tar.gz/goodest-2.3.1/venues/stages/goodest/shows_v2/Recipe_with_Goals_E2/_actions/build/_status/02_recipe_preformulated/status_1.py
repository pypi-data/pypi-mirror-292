















''''
	python3 status.proc.py shows_v2/Recipe_with_Goals_E2/_actions/build/_status/02_recipe_preformulated/status_1.py
"'''

#|
#
from goodest.shows_v2.treasure.nature.land.grove._ops.seek_name_or_accepts import seek_name_or_accepts
from goodest.shows_v2.Recipe_with_Goals_E2._actions.build import build_recipe_with_goals
#\
#/
#	goals
#
from goodest.adventures.monetary.DB.goodest_tract.goals.retrieve_one import retrieve_one_goal
#\
#/
#	foods
#
import goodest.besties.food_USDA.deliveries.one.assertions.foundational as assertions_foundational
import goodest.besties.food_USDA.examples as USDA_examples	
import goodest.besties.food_USDA.nature_v2 as food_USDA_nature_v2
#\
#/
#	supps
#
import goodest.besties.supp_NIH.nature_v2 as supp_NIH_nature_v2
import goodest.besties.supp_NIH.examples as NIH_examples
#\
#/
import goodest.mixes.insure.equality as equality
#
#	
import rich
#
#
from fractions import Fraction
from copy import deepcopy
import json
#
#|


	
def add (path, data):
	import pathlib
	from os.path import dirname, join, normpath
	this_directory = pathlib.Path (__file__).parent.resolve ()
	example_path = normpath (join (this_directory, path))
	FP = open (example_path, "w")
	FP.write (data)
	FP.close ()
	
def check_1 ():
	goal_emblem = "14"

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
	add (
		"status_1.JSON", 
		json.dumps (recipe_packet, indent = 4)
	)
	essential_nutrients_grove = recipe_packet ["essential nutrients"] ["grove"]

	
	'''
		Dietary Fiber
	
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

	
def check_2 ():
	goal_emblem = "14"

	recipe_packet = build_recipe_with_goals ({
		"IDs_with_amounts": [
			{
				"FDC_ID": "1795141",
				"packages": 2
			}
		],
		"goals": retrieve_one_goal ({
			"emblem": goal_emblem
		}) ["nature"]
	})
	add (
		"status_1.JSON", 
		json.dumps (recipe_packet, indent = 4)
	)
	essential_nutrients_grove = recipe_packet ["essential nutrients"] ["grove"]

	
	'''
		Dietary Fiber
	
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
		"227/35"
	), dietary_RDA_Earth_days
	assert (
		dietary_RDA_Earth_days ["sci note string"] ==
		"6.4857e+0"
	), dietary_fiber
	
	
	
checks = {
	"Check 1": check_1,
	"Check 2": check_2	
}
