




'''
	# Status: Untested

	from goodest.adventures.monetary.DB.goodest_inventory._treasures.document.find import find_treasure
	find_treasure ({
		"collection": "food",
		"filter": {
			"nature.identity.FDC ID": ""
		}
	})
'''

	
from goodest._essence import retrieve_essence
from goodest.adventures.monetary.DB.goodest_inventory.connect import connect_to_goodest_inventory
from goodest.besties.food_USDA.nature_v2._ops.retrieve import retrieve_parsed_USDA_food
	
import ships.modules.exceptions.parse as parse_exception
	
	

def find_treasure (packet):
	filter = packet ["filter"]
	collection_name = packet ["collection"]
	
	treasure = None
	
	try:
		[ driver, goodest_inventory_DB ] = connect_to_goodest_inventory ()
		collection = goodest_inventory_DB [ collection_name ]
	except Exception as E:
		print ("treasure collection connect:", E)
		raise Exception (E)
	
	try:	
		essence = retrieve_essence ()
		treasure = collection.find_one (filter, {"_id": 0});
		
	except Exception as E:
		print (parse_exception.now (E))
		raise Exception (E)
		
	try:
		driver.close ()
	except Exception as E:
		print (parse_exception.now (E))
		print ("treasure collection disconnect exception:", E)	
		
	return treasure;










