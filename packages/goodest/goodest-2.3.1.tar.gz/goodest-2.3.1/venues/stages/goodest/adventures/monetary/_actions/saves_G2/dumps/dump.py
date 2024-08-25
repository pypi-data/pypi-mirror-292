
#----
#
from goodest._essence import retrieve_essence
import goodest.mixes.procedure as procedure
from goodest.adventures.monetary.moves.retrieve_collections import retrieve_collections
from goodest.adventures.monetary.moves.retrieve_collections_G2 import retrieve_collections_G2
#
#
import click
import rich
#
#
import pathlib
from os.path import dirname, join, normpath
import sys
import os
import time
#
#----




def etch (bracket, name):
	import pathlib
	from os.path import dirname, join, normpath
	this_directory = pathlib.Path (__file__).parent.resolve ()
	the_path = normpath (join (this_directory, name))

	from goodest.mixes.drives.etch.bracket import etch_bracket
	etch_bracket (the_path, bracket)

def dump_node (packet):
	version = packet ["version"]
	database_names = packet ["database_names"]
	
	
	#
	#
	#	essence
	#	
	#
	essence = retrieve_essence ()
	the_dumps_path = essence ["monetary"] ["saves_G2"] ["dumps"] ["path"]
	URL = essence ["monetary"] ["URL"]
	
	
	#
	#
	#	calculated
	#
	#
	collections = retrieve_collections (database_names);
	dumps_note_path = str (normpath (join (
		the_dumps_path, 
		version,
		"Node.JSON"
	)))
	
	#
	#
	#	Check if that version already exists
	#
	#
	dump_version_path = str (normpath (join (
		the_dumps_path, 
		version
	)))
	if (os.path.exists (dump_version_path) == True):
		rich.print_json (data = {
			"already_exists": dump_version_path
		})	
		return;
	

	''''
		records = {
			"databases": [{
				"name": "",
				"collections": [{
					"name": "",
					"path": ""
				}]
			}]
		}
	
	"'''
	records = {
		"databases": []
	}
	
	
	node_structure = retrieve_collections_G2 (
		database_names = database_names
	);
	
	rich.print_json (data = {
		"node_structure": node_structure
	})	
	
	for database in node_structure ["databases"]:
		database_name = database ["name"]
		database_path = str (normpath (join (
			the_dumps_path, 
			version,
			database_name
		)))
		
		collections = database ["collections"]
		
		os.makedirs (database_path, exist_ok = True)	
		
		for collection in collections:
			collection_name = collection ["name"]
			collection_path_name = collection_name + "." + "collection.dump.gzip"
			
			save_path = str (normpath (join (database_path, collection_path_name)))
			collection ["path"] = collection_path_name
			
			process_strand = [
				"mongodump",
				"--uri",
				URL,
				f"--db={ database_name }",
				f"--collection={ collection_name }",
				"--gzip",
				f"--archive={ save_path }"
			]
			procedure.go (script = process_strand)
			
			time.sleep (.25)
			print ()
			
			
	rich.print_json (data = {
		"node_structure": node_structure
	})
	
	os.system (f"chmod -R 777 '{ dump_version_path }'")

