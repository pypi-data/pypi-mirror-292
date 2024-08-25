



''''
return {
	"labels": [
		"carbohydrates"
	],
	"goal": {
		"mass + mass equivalents": {
			"per Earth day": {
				"grams": {
					"fraction string": "275",
					"decimal string": "2.7500e+2"
				},
				"portion": {
					"fraction string": "1375000000/2309920787",
					"percent string": "59.52585074511475"
				}
			}
		}
	},
	"qualities": [{
		"labels": [
			"Dietary Fiber"
		],
		"goal": {
			"mass + mass equivalents": {
				"per Earth day": {
					"grams": {
						"fraction string": "28"
					}
				}
			}
		}
	}]
}
"'''

'''
	200 pounds = 90000 grams
		
		275 / 90000 
			= 0.00306
			= 0.306%
'''

def Carbohydrates (packet):
	qualities = packet ["qualities"]

	return {
		"labels": [
			"Carbohydrates", "Total Carbohydrates"
		],
		
		"criteria": {
			"RDA": {
				"mass + mass equivalents": {
					"per Earth day": {
						"grams": {
							"fraction string": "275"
						}
					}
				}
			},
		},
		
		"references": [
			"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
		],
		
		"qualities": qualities
	}