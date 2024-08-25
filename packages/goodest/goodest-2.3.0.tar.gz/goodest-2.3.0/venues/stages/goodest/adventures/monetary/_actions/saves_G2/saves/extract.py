#\
#
import pathlib
from os.path import dirname, join, normpath
import sys
import os
import time
import json
#
#
import click
import rich
#
#
from goodest._essence import retrieve_essence
import goodest.mixes.procedure as procedure
#
#/

from goodest.adventures.monetary.moves.drop_database import drop_database
	

def scan_record (path):
	with open (path, 'r') as FP:
		record = json.load (FP)

	return record

def run_procedure (process_strand):
	print ()
	print ("procedure:", process_strand)
	procedure.go (script = process_strand)
	time.sleep (.25)

def extract_node (packet):
	#
	#
	#	packets
	#
	#
	version = packet ["version"]
	format = packet ["format"]
	wipe = packet ["wipe"]

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
	
	##
	#
	#	Calculated
	#		1. Calculate the note path
	#		2. Calculate the path of this version of the save.
	#		3. Calculate the path of the node structure.
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
	if (os.path.exists (the_version_path) != True):
		rich.print_json (data = {
			"does not exist": the_version_path
		})	
		return;
		
	node_structure_path = str (normpath (join (
		the_version_path, 
		"Node.JSON"
	)))
	node_structure = scan_record (node_structure_path)
	#
	#/
	

	rich.print_json (data = {
		"node_structure": node_structure
	})
	
	
	for database in node_structure ["databases"]:
		database_name = database ["name"]
		database_path = str (normpath (join (
			the_version_path,
			database_name
		)))
		
		if (wipe == "yes"):
			drop_database (database_name)
			
		#continue;
		
		collections = database ["collections"]
		
		os.makedirs (database_path, exist_ok = True)	
		
		for collection in collections:
			collection_name = collection ["name"]
			
			if (format == "dump"):
				collection_dump_path_name = collection_name + "." + "collection.dump.gzip"
				collection_dump_path = str (normpath (join (database_path, collection_dump_path_name)))
				collection ["dump_path"] = collection_dump_path_name
			
				run_procedure ([
					"mongorestore",
					"--uri",
					URL,
					f"--db={ database_name }",
					f"--collection={ collection_name }",
					"--gzip",
					f"--archive={ collection_dump_path }"
				])
			
			elif (format == "export"):
				collection_export_path_name = collection_name + "." + "collection.export"
				collection_export_path = str (normpath (join (database_path, collection_export_path_name)))
				collection ["export_path"] = collection_export_path_name
				
				run_procedure ([
					"mongoimport",
					"--uri",
					URL,
					f"--db={ database_name }",
					f"--collection={ collection_name }",
					f"--file={ collection_export_path }"
				])
