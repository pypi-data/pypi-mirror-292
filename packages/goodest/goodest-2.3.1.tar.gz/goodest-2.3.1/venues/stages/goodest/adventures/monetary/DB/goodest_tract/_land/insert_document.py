
'''
	import goodest.adventures.monetary.DB.goodest_tract._land.insert_document as _land_insert_document
	_land_insert_document.smoothly ({
		"collection": "cautionary_ingredients",
		"document": {},
		"add_region": True
	})
'''

'''
	itinerary:
		https://www.mongodb.com/docs/manual/core/aggregation-pipeline/
		region = highest region number + 1
'''

from goodest.adventures.monetary.DB.goodest_tract.connect import connect_to_goodest_tract

def smoothly (packet):
	document = packet ["document"]
	collection_name = packet ["collection"]
	
	if ("add_region" in packet):
		add_region = packet ["add_region"]
	else:
		add_region = False
	
	[ driver, goodest_tract_DB ] = connect_to_goodest_tract ()
	collection = goodest_tract_DB [ collection_name ]
	
	
	if (add_region):
		#
		#	find the max region number and add 1
		#
		#
		result = list (
			collection.aggregate ([
				{
					"$group": {
						"_id": None, 
						"max_region": {
							"$max": "$region"
						}
					}
				}
			])
		)
		region = result [0] ['max_region'] + 1 if result else 1
		
		print ('region:', region)
		
		proceeds = collection.insert_one ({
			** document,
			"region": region
		})
		
	else:
		proceeds = collection.insert_one (document)
		
	driver.close ()
	
	return proceeds;
