



'''
	from goodest.adventures.monetary.DB.goodest_inventory.supps.document.enhance_nature import enhance_supp_nature
	enhance_supp_nature ({
		"DSLD_ID": DSLD_ID,
		"filter": {
			"nature.identity.DSLD ID": ""
		}
	})
'''


#\
#
import ships.modules.exceptions.parse as parse_exception
#
#
from goodest._essence import retrieve_essence
from goodest.adventures.monetary.DB.goodest_inventory.connect import connect_to_goodest_inventory
from goodest.besties.supp_NIH.nature_v2._ops.retrieve import retrieve_parsed_NIH_supp
#
#/

from goodest.adventures.monetary.DB.goodest_inventory.supps.document.find import find_supp
import goodest.besties.supp_NIH.nature_v2 as supp_NIH_nature_v2

	

def enhance_supp_nature (packet):
	filter = packet ["filter"]
	DSLD_ID = packet ["DSLD_ID"]
	origin = packet ["origin"]

	collection_name = "supp"

	update_proceeds = None

	try:
		[ driver, goodest_inventory_DB ] = connect_to_goodest_inventory ()
		collection = goodest_inventory_DB [ collection_name ]
	except Exception as E:
		print ("enhance_nature collection connect:", E)
		raise Exception (E)
	
	
	if (origin == "source"):
		#\
		#
		essence = retrieve_essence ()
		key = essence ['NIH'] ['supp']
		out_packet = retrieve_parsed_NIH_supp ({
			"DSLD_ID": DSLD_ID,
			"NIH API Pass": key,
			"format": 2
		})
		if ('anomaly' in out_packet):
			raise Exception (out_packet ['anomaly'])
		
		nature = out_packet ["nature"];
		NIH_supp = out_packet ["NIH supp"];
		
		update = {
			'$set': {
				'nature': nature,
				'NIH supp': NIH_supp
			}
		}
		
		update_proceeds = collection.update_one (filter, update);
		#
		#/
		
	elif (origin == "saved"):
		supp = find_supp ({
			"filter": {
				"nature.identity.DSLD ID": DSLD_ID
			}
		})

		NIH_supp_data = supp ["NIH supp"] ["data"]
		nature = supp_NIH_nature_v2.create (NIH_supp_data);

		update = {
			'$set': {
				'nature': nature
			}
		}
	
		update_proceeds = collection.update_one (filter, update);
		
	else:
		raise Exception (f"Origin '{ origin }' was not accounted for.")
	

		

		
	try:
		driver.close ()
	except Exception as E:
		print (parse_exception.now (E))
		print ("enhance_nature collection disconnect exception:", E)	
		
	return update_proceeds;








