















''''
	python3 status.proc.py shows_v2/Recipe_with_Goals_E2/_actions/build/_status/1_2_recipe_preformulated/status_1.py
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



def find_grams (measures):
	return Fraction (
		measures ["mass + mass equivalents"] ["per recipe"] ["grams"] ["fraction string"]
	)
	
def add (path, data):
	import pathlib
	from os.path import dirname, join, normpath
	this_directory = pathlib.Path (__file__).parent.resolve ()
	example_path = normpath (join (this_directory, path))
	FP = open (example_path, "w")
	FP.write (data)
	FP.close ()
	
def retrieve_supp (supp_path):
	return supp_NIH_nature_v2.create (
		NIH_examples.retrieve (supp_path) 
	)

def retrieve_food (food_path):
	return food_USDA_nature_v2.create (
		USDA_examples.retrieve (food_path)
	)

def check_1 ():
	goal_emblem = "14"

	recipe_packet = build_recipe_with_goals ({
		"IDs_with_amounts": [
			{
				"FDC_ID": "2025440",
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
	return;
	
	'''
		{
			"days of ingredient": {
				"mass + mass equivalents": {
					"per recipe": {
						"fraction string": "90/13",
						"decimal string": "6.923"
					}
				}
			}
		}
	'''
	calcium = seek_name_or_accepts (
		grove = essential_nutrients_grove,
		name_or_accepts = "calcium"
	)
	assert (
		calcium ["goal"]["days of ingredient"]["mass + mass equivalents"]["per recipe"]["fraction string"] ==
		"90/13"
	)
	assert (
		calcium ["goal"]["days of ingredient"]["mass + mass equivalents"]["per recipe"]["decimal string"] ==
		"6.923"
	)
	
	#print ("calcium:", calcium)

	
	
	
	
	
	
checks = {
	"check 1": check_1
}
