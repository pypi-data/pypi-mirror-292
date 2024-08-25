



#/
#
import goodest.measures.number.decimal.reduce as reduce_decimal
from goodest.adventures.alerting.parse_exception import parse_exception
from goodest.adventures.alerting import activate_alert	
from goodest.shows_v2.goals._plays.find_quality_with_label import find_quality_with_label
#
from .find_goal_in_goals import find_goal_in_goals
from .add_attained import add_attained
#
#
from ships.flow.simultaneous_v2 import simultaneously_v2
#
#
import rich
#
#
import time
from fractions import Fraction
import copy
#
#\

''''
	returns:
		skipped_composition
		goal not found for
"'''

#
#	quality = ingredient, nutrient, etc.
#	
#		for example: carbohydrates is a quality.
#

import rich

def add_goals (packet):
	essential_nutrients_grove = packet ["essential_nutrients_grove"]
	goals = packet ["goals"]
	records = packet ["records"]
	
	return_packet = {
		"goal not found for": []
	}
	
	def move (grove_quality):
		assert ("info" in grove_quality), grove_quality
		assert ("names" in grove_quality ["info"]), grove_quality
		
		grove_quality_names = grove_quality ["info"] ["names"]
		grove_quality ["goal"] = {}
		
		goal = None;
		try:		
			goal_quality = find_quality_with_label (
				goals ["qualities"], 
				grove_quality_names
			)
			
			print ("goal quality found.", goal_quality)
			
			grove_quality ["goal"] = goal_quality
			
			#
			#	Calculate how much of the goal was attained.
			#
			#
			add_attained (grove_quality)
			
			
			
		except Exception as E:	
			print ("goal quality not found.", grove_quality_names, E)
			return_packet ["goal not found for"].append (grove_quality_names)
		
		
		
		#
		#	Recursively search through the "unites"
		#
		#
		if ("unites" in grove_quality):
			simultaneously_v2 (
				items = grove_quality ["unites"],
				capacity = 10,
				move = move
			)

		
		return;

	def add_goals_to_recipe (essential_nutrients_grove):
		simultaneously_v2 (
			items = essential_nutrients_grove,
			capacity = 10,
			move = move
		)

	add_goals_to_recipe (essential_nutrients_grove)

