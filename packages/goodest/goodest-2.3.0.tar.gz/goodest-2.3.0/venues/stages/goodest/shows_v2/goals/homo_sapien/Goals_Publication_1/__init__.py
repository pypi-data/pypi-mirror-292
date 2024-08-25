
'''
	from goodest.shows_v2.goals.homo_sapien.Goals_Publication_1 import build_Goals_Publication_1
	goals = build_Goals_Publication_1 ()
'''

'''
	multikey index:
		https://www.mongodb.com/docs/manual/core/indexes/index-types/index-multikey/
'''

''''

grove: [{
	"goal": {
		"quest": {
			"labels": [],
			"RDA": [],
			"UL": [],
			"notes": [],
			"references": []
		},
		"days of ingredient": {
			"mass + mass equivalents": {
				"per recipe": {
					"fraction string": "47524235067827163/87960930222080000",
					"decimal string": "0.540"
				}
			}
		}
	}

"'''

''''
{
	"labels": [
		"Biotin"
	],
	"goal": {
		#
		#	RDA
		#
		#		
		"mass + mass equivalents": {
			"per Earth day": {
				"grams": {
					"fraction string": "3/100000",
					"decimal string": "3.0000e-5"
				},
				"portion": {
					"fraction string": "150/2309920787",
					"percent string": "6.493729172194336e-06"
				}
			}
		}
	}
}

"'''

#\
#
import copy
#
#
from goodest.shows_v2.Recipe_with_Goals_E2._actions.build import build_recipe_with_goals
from goodest.shows_v2.recipe._ops.retrieve import retrieve_recipe
#
#
from .info import retrieve_info
from .procedures.measure_portions import measure_portions
from .procedures.measure_sci_note_strings import measure_sci_note_strings
#
#/

def build_Goals_Publication_1 ():
	goals = retrieve_info ()

	measure_sci_note_strings (goals) 
	
	#
	#	portions
	#
	
	#portion_evalutaion = measure_portions (goals) 
	#print ("portion evaluation exceptions:", portion_evalutaion ["exceptions"])
	
	recipe_with_goals = build_recipe_with_goals ({
		"IDs_with_amounts": [],
		"goals": goals
	})
	goals ["recipe"] = recipe_with_goals
	
	#
	#
	#	portion evaluation
	#
	#
	land = copy.deepcopy (goals ["recipe"] ["essential nutrients"])
	portion_evalutaion = measure_portions (land) 
	
	goals ["recipe"] ["essential nutrients"] = land;
	

	
	return goals;