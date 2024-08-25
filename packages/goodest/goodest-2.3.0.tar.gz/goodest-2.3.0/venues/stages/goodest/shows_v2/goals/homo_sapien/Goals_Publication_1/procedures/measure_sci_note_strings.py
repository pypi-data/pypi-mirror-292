

from fractions import Fraction
import goodest.measures.number.sci_note_2 as sci_note_2

def measure_sci_note_strings (goals):
	qualities = goals ["qualities"]

	for quality in qualities:
		try:
			RDA = quality ["criteria"] ["RDA"];
			
			if ("mass + mass equivalents" in RDA):
				RDA_grams = Fraction (
					RDA ["mass + mass equivalents"] ["per Earth day"] ["grams"] ["fraction string"]
				)
				RDA ["mass + mass equivalents"] ["per Earth day"] ["grams"] ["sci note string"] = sci_note_2.produce (RDA_grams)
				
			if ("energy" in RDA):
				RDA_Food_Calories = Fraction (
					RDA ["energy"] ["per Earth day"] ["Food Calories"] ["fraction string"]
				)
				RDA ["energy"] ["per Earth day"] ["Food Calories"] ["sci note string"] = sci_note_2.produce (RDA_Food_Calories)	
				
		except Exception as E:
			print ("mass + mass eq sum exception:", {
				"E": E,
				"quality": quality
			})
