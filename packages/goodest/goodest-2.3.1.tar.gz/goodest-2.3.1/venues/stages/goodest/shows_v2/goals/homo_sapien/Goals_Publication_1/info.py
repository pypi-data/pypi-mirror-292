

''''
	200 pounds = 90000 grams
		
		462 / 90000 
			= 0.00513
			= 0.513%
			
	That means:
		Eat 1/200th of body weight per day.
			(to sustain healthy lifestyle)
"'''

from .Ingredients.Biotin import Biotin
from .Ingredients.Calcium import Calcium
from .Ingredients.Calories import Calories
from .Ingredients.Carbohydrates import Carbohydrates
from .Ingredients.Chloride import Chloride
from .Ingredients.Choline import Choline
from .Ingredients.Cholesterol import Cholesterol
from .Ingredients.Chromium import Chromium
from .Ingredients.Dietary_Fiber import Dietary_Fiber
from .Ingredients.Fats import Fats
from .Ingredients.Saturated_Fat import Saturated_Fat

def retrieve_info ():
	return {
		"label": "Prototype Goals for the Average Adult Homo Sapiens, Publication 1",
		"cautions": [
			"The goals for each individual adult may vary substantially based on body, lifestyle, and aspirations.",
			"Consulting with your nutritionist or physician is recommended."
		],
		"qualities": [
			Biotin (),
			Calcium (),
			Calories (),
			Carbohydrates ({
				"qualities": []
				#"qualities": [
				#	Dietary_Fiber ()
				#]
			}),
			Dietary_Fiber (),
			Chloride (),
			Cholesterol (),
			Choline (),		
			Chromium (),
			Fats ({
				"qualities": []
				#"qualities": [
				#	Saturated_Fat ()
				#]
			}),
			Saturated_Fat (),
			{
				"labels": [
					"Copper"
				],
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "9/10000"
								}
							}
						}
					},
				},
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Folate",
					"Folic Acid"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "1/2500"
								}
							}
						}
					},
				},
				
				"notes": [
					"400mcg DFE (Dietary Folate Equilavent)"
				],
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Iodine"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "3/20000"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Iron"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "9/500"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Magnesium"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "21/50"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Manganese"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "23/10000"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Molybdenum"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "9/200000"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Niacin"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "2/125"
								}
							}
						}
					},
				},
				
				"notes": [
					"16mg NE"
				],
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Pantothenic Acid"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "1/200"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Phosphorus"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "5/4"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Potassium"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "47/10"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Protein"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "50"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Riboflavin"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "13/10000"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Selenium"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "11/200000"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Sodium"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "23/10"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Thiamin"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "3/2500"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Vitamin A"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "9/10000"
								}
							}
						}
					},
				},
				
				"notes": [
					"900mcg RAE"
				],
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Vitamin B6"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "17/10000"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Vitamin B12"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "3/1250000"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Vitamin C"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "9/100"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Vitamin D"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "1/50000"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Vitamin E"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "3/200"
								}
							}
						}
					},
				},
				
				"notes": [
					"15mg alpha-tocopherol"
				],
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Vitamin K"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "3/25000"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			},
			{
				"labels": [
					"Zinc"
				],
				
				"criteria": {
					"RDA": {
						"mass + mass equivalents": {
							"per Earth day": {
								"grams": {
									"fraction string": "11/1000"
								}
							}
						}
					},
				},
				
				"references": [
					"https://www.fda.gov/food/nutrition-facts-label/daily-value-nutrition-and-supplement-facts-labels"
				]
			}
		],
		"limiters": [
			{
				"label": "species",
				"includes": [
					"Homo Sapien"
				]
			},
			{
				"kind": "slider--integer",
				"label": "age",
				"includes": [
					[
						"20",
						"eternity"
					]
				]
			},
			{
				"label": "exclusions",
				"includes": [
					"pregnant",
					"breast feeding"
				]
			}
		],
		"sources": [
			"https://www.fda.gov/food/new-nutrition-facts-label/daily-value-new-nutrition-and-supplement-facts-labels",
			"https://www.fda.gov/food/nutrition-facts-label/calories-nutrition-facts-label",
			"https://www.fda.gov/media/99069/download",
			"https://www.fda.gov/media/99059/download"
		]
	}