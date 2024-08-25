


'''	
	from goodest.adventures.monetary.DB.goodest_inventory.connect import connect_to_goodest_inventory, disconnect
	[ driver, goodest_inventory_DB ] = connect_to_goodest_inventory ()
	driver.close ()
'''

'''
	from goodest.adventures.monetary.DB.goodest_inventory.connect import connect_to_goodest_inventory
	[ driver, goodest_inventory_DB ] = connect_to_goodest_inventory ()
	foods_collection = goodest_inventory_DB ["foods"]	
	foods_collection.close ()
'''


#\
#
import pymongo
#
#
import ships.modules.exceptions.parse as parse_exception
#
#
from goodest.adventures.monetary.moves.URL.retrieve import retreive_monetary_URL
from goodest._essence import retrieve_essence
#
#/

def connect_to_goodest_inventory ():
	essence = retrieve_essence ()
	
	ingredients_DB_name = essence ["monetary"] ["databases"] ["goodest_inventory"] ["alias"]
	
	monetary_URL = retreive_monetary_URL ()

	driver = pymongo.MongoClient (monetary_URL)

	return [
		driver,
		driver [ ingredients_DB_name ]
	]
	
def disconnect (driver):
	try:
		driver.close ()
	except Exception as E:
		print (parse_exception.now (E))
		print ("treasure collection disconnect exception:", E)	