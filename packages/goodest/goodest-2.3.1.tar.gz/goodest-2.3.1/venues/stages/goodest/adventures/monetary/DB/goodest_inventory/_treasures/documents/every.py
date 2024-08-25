




'''
	from goodest.adventures.monetary.DB.goodest_inventory.foods.document.every import find_every_treasure
	[ FDC_IDs, Skipped ] = find_every_treasure ({
		"collection": food,
		"path": "nature.identity.FDC ID"
	})
'''

	
	
from goodest._essence import retrieve_essence
from goodest.adventures.monetary.DB.goodest_inventory.connect import connect_to_goodest_inventory
from goodest.besties.food_USDA.nature_v2._ops.retrieve import retrieve_parsed_USDA_food
	
import ships.modules.exceptions.parse as parse_exception
	
import pydash
	
	
'''
	FDC_ID = "",
	affiliates = [],
	goodness_certifications = []
'''
def find_every_treasure (packet):
	path = packet ["path"]
	collection_name = packet ["collection"]
	
	ID_Scroll = []
	Skipped = []	
	
	try:
		[ driver, goodest_inventory_DB ] = connect_to_goodest_inventory ()
		collection = goodest_inventory_DB [ collection_name ]
	except Exception as E:
		print ("collection connect exception:", E)
		raise Exception (E)
	
	try:	
		essence = retrieve_essence ()
		groceries = collection.find ({}, { "_id": 0 });
		for grocery in groceries:
			try:
				ID = pydash.get (grocery, path)
				
				if (type (ID) == str):
					ID_Scroll.append (ID)
				else:
					print ("grocery:", grocery)
				
				
			except Exception as E1:
				print ("exception:", E1, grocery)
				Skipped.append (grocery)
		
	except Exception as E:
		print (parse_exception.now (E))
		raise Exception (E)
		
	try:
		driver.close ()
	except Exception as E:
		print (parse_exception.now (E))
		print ("collection disconnect exception:", E)	
		
	return [ ID_Scroll, Skipped ];








