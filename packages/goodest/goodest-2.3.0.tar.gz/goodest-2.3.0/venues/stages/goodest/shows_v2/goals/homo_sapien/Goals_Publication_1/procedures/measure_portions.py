

''''
	"grove": [{
		"goal": {
			"criteria": {
				"RDA": {
					"mass + mass equivalents": {
						"per Earth day": {
							"grams": {
								"fraction string": "3/2500"
								
	}]

"'''

import goodest.measures.number.sci_note_2 as sci_note_2

from fractions import Fraction

def measure_portions (land):
	grove = land ["grove"]


	#
	#
	#	returns
	#
	#
	exceptions = []
	mass_plus_mass_equivalents_sum = 0
	
	
	
	#
	#	This adds to the "sum" mass_plus_mass_equivalents_sum.
	#
	#
	for quality in grove:
		try:
			RDA = quality ["goal"] ["criteria"] ["RDA"];
			
			if ("mass + mass equivalents" in RDA):
				mass_plus_mass_equivalents_sum += Fraction (
					RDA ["mass + mass equivalents"] ["per Earth day"] ["grams"] ["fraction string"]
				)
				
		except Exception as E:
			print ("mass + mass eq sum exception:", {
				"E": E,
				"quality": quality
			})
			exceptions.append (quality)
	
	#
	#
	#
	#
	#
	land ["goals"] = {
		"sum": {
			"mass + mass equivalents": {
				"per Earth day": {
					"grams": {
						"fraction string": str (mass_plus_mass_equivalents_sum),
						"decimal string": sci_note_2.produce (mass_plus_mass_equivalents_sum)
					}
				}
			}
		}
	}
	
	
	#
	#
	#	This calculates the fractions of the entire goal of each quality goal.
	#
	#
	for quality in grove:
		try:
			RDA = quality ["goal"] ["criteria"] ["RDA"];
			
			if ("mass + mass equivalents" in RDA):
				amount = RDA ["mass + mass equivalents"] ["per Earth day"] ["grams"] ["fraction string"];
				
				portion = str (Fraction (amount) / Fraction (mass_plus_mass_equivalents_sum))
				percent = str (float (Fraction (portion) * 100))
			
				RDA ["mass + mass equivalents"] ["per Earth day"] ["portion"] = {
					"fraction string": portion,
					"sci note percent string": sci_note_2.produce (percent) + "%",
					"decimal string": sci_note_2.produce (percent)
				}

		except Exception as E:
			print ("mass + mass eq portion exception:", {
				"E": E,
				"quality": quality
			})
		
			exceptions.append (quality)
			
	return {
		"exceptions": exceptions
	}