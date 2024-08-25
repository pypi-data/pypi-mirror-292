

''''
	from goodest.adventures.monetary.moves.retrieve_collections import retrieve_collections
	collections = retrieve_collections (
		database_names = []
	);
"'''


'''
	Get Collections:
	
		
'''

from goodest.adventures.monetary.moves.URL.retrieve import retreive_monetary_URL
from goodest._essence import retrieve_essence
	
import pymongo

''''
	"monetary": {
		"databases": {
			"goodest_inventory": {
				"alias": "goodest_inventory",
"'''
''''
def retrieve_database_names ():
	essence = retrieve_essence ()

	database_names = []

	databases = essence ["monetary"] ["databases"]
	for database_entry in databases:
		print ("database_entry:", database_entry)
	
		database_names.append (
			databases [ database_entry ][ "alias" ]
		)

	return database_names;
"'''
	

def retrieve_collections (
	database_names = []
):
	essence = retrieve_essence ()
	monetary_URL = retreive_monetary_URL ()
	
	proceeds = [
		# [ "db", "collection" ]
	]
	
	driver = pymongo.MongoClient (monetary_URL)
	
	#database_names = retrieve_database_names ()
	#print ("database_names:", database_names)
	
	
	for database_name in database_names:
		collections = driver [ database_name ].list_collection_names ()
		
		for collection_name in collections:
			print ("collection_name:", collection_name)
		
			proceeds.append ([
				database_name,
				collection_name
			])
		
	driver.close ()
	
	return proceeds;