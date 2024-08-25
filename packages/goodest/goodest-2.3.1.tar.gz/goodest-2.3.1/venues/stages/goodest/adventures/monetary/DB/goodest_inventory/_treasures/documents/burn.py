
'''
	from goodest.adventures.monetary.DB.goodest_inventory._treasures.documents.burn import burn_treasure
	burn_treasure ({
		"collection": "",
		"filter": {
		
		}
	})
'''


from goodest._essence import retrieve_essence
from goodest.adventures.monetary.DB.goodest_inventory.connect import connect_to_goodest_inventory, disconnect
from goodest.besties.food_USDA.nature_v2._ops.retrieve import retrieve_parsed_USDA_food
	
import ships.modules.exceptions.parse as parse_exception
	
	

def burn_treasure (packet):
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
		treasure = collection.delete_one (filter);
		
	except Exception as E:
		print (parse_exception.now (E))
		raise Exception (E)
		
	disconnect (driver)
		
	return treasure;





