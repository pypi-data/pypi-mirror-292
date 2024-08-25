


def Fats (packet):
	qualities = packet ["qualities"]
	return {
		"labels": [
			"Fats", "Fat"
		],
		
		"criteria": {
			"RDA": {
				"mass + mass equivalents": {
					"per Earth day": {
						"grams": {
							"fraction string": "78"
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