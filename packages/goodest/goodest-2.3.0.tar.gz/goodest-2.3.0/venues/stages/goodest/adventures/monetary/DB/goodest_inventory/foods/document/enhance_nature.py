



'''
	from goodest.adventures.monetary.DB.goodest_inventory.foods.document.enhance_nature import enhance_food_nature
	enhance_nature ({
		"origin": "saved",
		
		"FDC_ID": FDC_ID,
		"filter": {
			"nature.identity.FDC ID": ""
		}
	})
'''
'''
	origin:
		saved: used the saved info
		source: ask for fresh info
'''


#\
#
import ships.modules.exceptions.parse as parse_exception
#
#
from goodest._essence import retrieve_essence
from goodest.adventures.monetary.DB.goodest_inventory.connect import connect_to_goodest_inventory
from goodest.besties.food_USDA.nature_v2._ops.retrieve import retrieve_parsed_USDA_food
from goodest.adventures.monetary.DB.goodest_inventory.foods.document.find import find_food
import goodest.besties.food_USDA.nature_v2 as food_USDA_nature_v2
#
#/

def enhance_food_nature (packet):
	filter = packet ["filter"]
	FDC_ID = packet ["FDC_ID"]
	
	if ("origin" in packet):
		origin = packet ["origin"]
	else:
		origin = "saved"

	collection_name = "food"

	update_proceeds = None

	try:
		[ driver, goodest_inventory_DB ] = connect_to_goodest_inventory ()
		food_collection = goodest_inventory_DB [ collection_name ]
	except Exception as E:
		print ("enhance_nature collection connect:", E)
		raise Exception (E)
	
	
	if (origin == "source"):
		#\
		#
		#
		#
		#
		essence = retrieve_essence ()
		USDA_food_pass = essence ['USDA'] ['food']
		out_packet = retrieve_parsed_USDA_food ({
			"FDC_ID": FDC_ID,
			"USDA API Pass": USDA_food_pass,
			"format": 2
		})
		if ('anomaly' in out_packet):
			raise Exception (out_packet ['anomaly'])
		
		nature = out_packet ["nature"];
		USDA_food = out_packet ["USDA food"];
		
		update = {
			'$set': {
				'USDA food': USDA_food,
				'nature': nature
			}
		}
		
		update_proceeds = food_collection.update_one (filter, update);
		#
		#/
		
	elif (origin == "saved"):
		food = find_food ({
			"filter": {
				"nature.identity.FDC ID": FDC_ID
			}
		})
		USDA_food_data = food ["USDA food"] ["data"]
	
		nature = food_USDA_nature_v2.create (
			USDA_food_data
		)
		update = {
			'$set': {
				'nature': nature
			}
		}
	
		update_proceeds = food_collection.update_one (filter, update);
		
	else:
		raise Exception (f"Origin '{ origin }' was not accounted for.")

		
	try:
		driver.close ()
	except Exception as E:
		print (parse_exception.now (E))
		print ("enhance_nature collection disconnect exception:", E)	
		
	return update_proceeds;








