

''''
from goodest.shows_v2.goals._plays.find_quality_with_label import find_quality_with_label
quality = find_quality_with_label (qualities, labels)
"'''

def find_quality_with_label (qualities, labels):
	for quality in qualities:
		for label in labels:
			for quality_label in quality ["labels"]:
				#print ("::::", label, quality_label)
			
				if (label.upper () == quality_label.upper ()):
					#print ("found")
				
					return quality;

	raise Exception (f"Quality '{ label }' was not found in the goal qualities.")