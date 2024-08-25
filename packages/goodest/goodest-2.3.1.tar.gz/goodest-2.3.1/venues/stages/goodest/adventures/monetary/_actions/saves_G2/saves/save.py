
#\
#
import pathlib
from os.path import dirname, join, normpath
import sys
import os
import time
#
#
import click
import rich
#
#
from goodest._essence import retrieve_essence
import goodest.mixes.procedure as procedure
from goodest.adventures.monetary.moves.retrieve_collections import retrieve_collections
from goodest.adventures.monetary.moves.retrieve_collections_G2 import retrieve_collections_G2
#
#/


def etch (bracket, name):
	import pathlib
	from os.path import dirname, join, normpath
	this_directory = pathlib.Path (__file__).parent.resolve ()
	the_path = normpath (join (this_directory, name))

	from goodest.mixes.drives.etch.bracket import etch_bracket
	etch_bracket (the_path, bracket)

def run_procedure (process_strand):
	print ()
	print ("procedure:", process_strand)
	procedure.go (script = process_strand)
	time.sleep (.25)

def save_node (packet):
	version = packet ["version"]
	database_names = packet ["database_names"]
	formats = packet ["formats"]
	
	#\
	#
	#	essence
	#	
	#
	essence = retrieve_essence ()
	the_saves_path = essence ["monetary"] ["saves_G2"] ["saves"] ["path"]
	URL = essence ["monetary"] ["URL"]
	#
	#/
	
	
	#\
	#
	#	calculated
	#		1. node_path
	#		2. Check if that version already exists
	#
	note_path = str (normpath (join (
		the_saves_path, 
		version,
		"Node.JSON"
	)))
	the_version_path = str (normpath (join (
		the_saves_path, 
		version
	)))
	if (os.path.exists (the_version_path) == True):
		rich.print_json (data = {
			"already_exists": the_version_path
		})	
		return;
	#
	#/
	

	
	
	node_structure = retrieve_collections_G2 (
		database_names = database_names
	);
	rich.print_json (data = {
		"node_structure": node_structure
	})	
	
	for database in node_structure ["databases"]:
		database_name = database ["name"]
		database_path = str (normpath (join (
			the_version_path,
			database_name
		)))
		
		collections = database ["collections"]
		
		os.makedirs (database_path, exist_ok = True)	
		
		for collection in collections:
			collection_name = collection ["name"]
			
			if ("dump" in formats):
				collection_dump_path_name = collection_name + "." + "collection.dump.gzip"
				collection_dump_path = str (normpath (join (database_path, collection_dump_path_name)))
				collection ["dump_path"] = collection_dump_path_name
				run_procedure ([
					"mongodump",
					"--uri",
					URL,
					f"--db={ database_name }",
					f"--collection={ collection_name }",
					"--gzip",
					f"--archive={ collection_dump_path }"
				])
			
			if ("export" in formats):
				collection_export_path_name = collection_name + "." + "collection.export"
				collection_export_path = str (normpath (join (database_path, collection_export_path_name)))
				collection ["export_path"] = collection_export_path_name
				run_procedure ([
					"mongoexport",
					"--uri",
					URL,
					f"--db={ database_name }",
					f"--collection={ collection_name }",
					f"--out={ collection_export_path }"
				])

			
			
	rich.print_json (data = {
		"node_structure": node_structure
	})
	etch (node_structure, note_path)
	
	os.system (f"chmod -R 777 '{ the_version_path }'")




