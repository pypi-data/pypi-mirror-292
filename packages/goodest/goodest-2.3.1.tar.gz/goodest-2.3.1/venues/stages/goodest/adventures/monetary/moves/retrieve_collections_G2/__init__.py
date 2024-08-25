

''''
	from goodest.adventures.monetary.moves.retrieve_collections_G2 import retrieve_collections_G2
	node_structure = retrieve_collections_G2 (
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
	
''''
	proceeds = {
		"databases": [{
			"name": "",
			"collections": [{
				"name": ""
			}]
		}]
	}
"'''
def retrieve_collections_G2 (
	database_names = []
):
	essence = retrieve_essence ()
	monetary_URL = retreive_monetary_URL ()

	
	node_structure = {
		"databases": []
	}
	
	driver = pymongo.MongoClient (monetary_URL)
	
	#database_names = retrieve_database_names ()
	#print ("database_names:", database_names)
	
	
	for database_name in database_names:
		DB_structure = {
			"name": database_name,
			"collections": []
		}
	
		collections = driver [ database_name ].list_collection_names ()
		print ("collections:", collections)
		
		for collection_name in collections:
			DB_structure ["collections"].append ({
				"name": collection_name
			})
			
			
		node_structure ["databases"].append (DB_structure)
		
	driver.close ()
	
	return node_structure;