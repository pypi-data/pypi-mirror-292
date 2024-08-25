

import law_dictionary
import ships.modules.exceptions.parse as parse_exception

def quest_questionaire (
	request,
	quests
):

	#
	#
	#	Check: JSON
	#
	#
	try:
		the_ask = request.json
	except Exception:
		return {
			"problem": {
				"label": "unfinished",
				"freight": {
					"description": "The body could not be parsed."
				}
			}
		}
	
	#
	#
	#	Check: label + freight
	#
	#
	try:
		report_1 = law_dictionary.check (
			return_obstacle_if_not_legit = True,
			allow_extra_fields = False,
			laws = {
				"label": {
					"required": True,
					"type": str
				},
				"freight": {
					"required": True,
					"type": dict
				}
			},
			dictionary = the_ask 
		)
		if (report_1 ["advance"] != True):
			return {
				"problem": {
					"label": "unfinished",
					"freight": {
						"description": "The packet check was not passed.",
						"report": report_1
					}
				}
			}
	except Exception as E:
		return {
			"problem": {
				"label": "unfinished",
				"freight": {
					"description": "An exception occurred while checking for the 'label' and the 'freight'.",
					"exception": parse_exception.now (E)
				}
			}
		}
	
	
	#
	#
	#	Check: label
	#
	#
	try:
		label = the_ask ["label"]		
		if (label not in quests):
			return {
				"problem": {
					"label": "unfinished",
					"freight": {
						"description": 'A quest with that "label" was not found.',
						"report": report_1
					}
				}
			}
	except Exception:
		return {
			"problem": {
				"label": "unfinished",
				"freight": {
					"description": "An exception occurred while searching for the label in the quests."
				}
			}
		}
		
	return {
		"the_ask": the_ask
	}
