

''''
	
"'''


''''
	TODO:
		monetary_saves
			exports
				1
					goodest_inventory
						food.JSON
						supp.JSON
						
					goodest_tract
"'''

#----
#
from goodest._essence import retrieve_essence
import goodest.mixes.procedure as procedure
from goodest.adventures.monetary.moves.retrieve_collections import retrieve_collections
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


def export_documents (packet):
	#
	#
	#	essence
	#
	#
	essence = retrieve_essence ()
	the_exports_path = essence ["monetary"] ["saves_G2"] ["exports"] ["path"]
	URL = essence ["monetary"] ["URL"]

	#
	#
	#	packets
	#
	#
	version = packet ["version"]
	database_names = packet ["database_names"]

	#
	#
	#	calculated
	#
	#
	export_note_path = str (normpath (join (
		the_exports_path, 
		version,
		"Node.JSON"
	)))
	
	collections = retrieve_collections (database_names);
	
	export_version_path = str (normpath (join (
		the_exports_path, 
		version
	)))
	if (os.path.exists (export_version_path) == True):
		rich.print_json (data = {
			"already_exists": export_version_path
		})	
		return;
	
	rich.print_json (data = {
		"export_note_path": export_note_path,
		"export_version_path": export_version_path,
		"collections": collections
	})
	
	
	#
	#
	#	the track
	#
	#
	already_exists = []
	for collection in collections:
		[ database_name, collection_name ] = collection
		
		name = collection_name + "." + "collection"
		export_path = str (normpath (join (
			the_exports_path, 
			version,
			database_name, 
			name
		)))
		if (os.path.exists (export_path) == True):
			already_exists.append (export_path)
			continue;
			
		process_strand = [
			"mongoexport",
			"--uri",
			URL,
			f"--db={ database_name }",
			f"--collection={ collection_name }",
			f"--out={ export_path }"
		]
		
		print (" ".join (process_strand))	
		
		procedure.go (
			script = process_strand
		)
		
		time.sleep (.25)
		print ()
	
	os.system (f"chmod -R 777 '{ the_exports_path }'")

	rich.print_json (data = {
		"already_exists": already_exists
	})	
	
	etch ({
		"collections": collections
	}, export_note_path)
	
