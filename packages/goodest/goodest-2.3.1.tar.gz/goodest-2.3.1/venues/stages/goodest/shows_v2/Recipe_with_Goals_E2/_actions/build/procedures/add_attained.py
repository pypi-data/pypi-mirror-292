



''''
{
	"info": {
		"includes": [],
		"names": [
			"protein"
		],
		"region": 1
	},
	"measures": {
		"mass + mass equivalents": {
			"per recipe": {
				"grams": {
					"fraction string": "20240865575263275/562949953421312",
					"scinote string": "3.5955e+1"
				}
			},
			"portion of grove": {
				"fraction string": "38100452847554400000/90807250222574431177",
				"scinote percentage string": "4.1958e+1"
			}
		}
	},
	"natures": [
		{
			"amount": "1",
			"source": {
				"name": "ORGANIC SOY BEANS",
				"FDC ID": "2025440",
				"UPC": "074873163285",
				"DSLD ID": ""
			},
			"ingredient": {
				"name": "Protein"
			},
			"measures": {
				"mass + mass equivalents": {
					"per package": {
						"listed": [
							"35.955",
							"g"
						],
						"grams": {
							"scinote string": "3.5955e+1",
							"decimal string": "35.955",
							"fraction string": "20240865575263275/562949953421312"
						}
					}
				}
			}
		}
	],
	"unites": [],
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
	
	#
	#	This is what is calculated.
	#
	#
	"attained": {
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
	}
}
"'''

from fractions import Fraction

import goodest.measures.number.sci_note_2 as sci_note_2
	

#
#	TODO:
#		Figure out how much of the goal was attained.
#
def add_attained (grove_quality):
	#
	#	grams:
	#
	#	
	try:
		if ("mass + mass equivalents" in grove_quality ["measures"]):			
			grams_per_recipe = (
				grove_quality ["measures"] ["mass + mass equivalents"] ["per recipe"] ["grams"] ["fraction string"]
			)
			grams_per_RDA = (
				grove_quality ["goal"] ["criteria"] ["RDA"] ["mass + mass equivalents"] ["per Earth day"] ["grams"] ["fraction string"]
			)
			attained_RDA = (
				Fraction (grams_per_recipe) / 
				Fraction (grams_per_RDA)
			)
			
			#
			#	RDA: Earth days
			#	UL: 
			#	LL:
			#
			''''
				Example:
					Where the recipe is 100% of the meals.
				
					UL:   2 Days
						Eating these meals in less than 2 days would be unhealthy.
						Overindulgence.
					
					RDA:  5 Days
						Eating these meals in 5 days is optimal.
						Perfect.
					
					LL:  11 Days
						Eating these meals in more than 11 days would be unhealthy.
						Malnurished
			"'''
			grove_quality ["attained"] = {
				"RDA": {
					"mass + mass equivalents": {
						"per recipe": {
							"Earth days": {
								"fraction string": str (attained_RDA),
								"sci note string": sci_note_2.produce (attained_RDA)
							}
						}
					}
				}
			}
			
	except Exception as E:
		print ("attained exception:", E)
