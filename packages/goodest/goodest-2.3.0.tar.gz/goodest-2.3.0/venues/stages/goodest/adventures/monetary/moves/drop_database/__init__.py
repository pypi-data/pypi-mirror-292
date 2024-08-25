

''''
	from goodest.adventures.monetary.moves.drop_database import drop_database
	drop_database ("")
"'''

from goodest.adventures.monetary.moves.URL.retrieve import retreive_monetary_URL
from goodest._essence import retrieve_essence
import pymongo

def drop_database (DB_name):
	essence = retrieve_essence ()
	monetary_URL = retreive_monetary_URL ()

	driver = pymongo.MongoClient (monetary_URL)
	proceeds = driver.drop_database (DB_name)
	print ("database drop results:", proceeds)


	driver.close ()