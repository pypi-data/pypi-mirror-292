


#\
#
import pathlib
from os.path import dirname, join, normpath
import sys
import os
import json
import time
import glob
#
#
import rich
import click
#
#
from goodest._essence import retrieve_essence
import goodest.mixes.procedure as procedure
from goodest.adventures.monetary.moves.retrieve_collections import retrieve_collections
#
#/


def scan_record (path):
	with open (path, 'r') as FP:
		record = json.load (FP)

	return record


def import_documents (packet):
	#
	#
	#	packets
	#
	#
	version = packet ["version"]
	drop = packet ["drop"]

	#
	#
	#	essence
	#
	#
	essence = retrieve_essence ()
	the_exports_path = essence ["monetary"] ["saves_G2"] ["exports"] ["path"]
	URL = essence ["monetary"] ["URL"]
	
	##
	#
	#	calculated
	#
	#
	export_record_path = str (normpath (join (
		the_exports_path, 
		version,
		"Node.JSON"
	)))
	collections_record = scan_record (export_record_path)
	collections = collections_record ["collections"]
	rich.print_json (data = {
		"export_record_path": export_record_path,
		"collections_record": collections_record
	})

	
	not_found = []
	for collection in collections:
		[ database_name, collection_name ] = collection
		
		name = collection_name + "." + "collection"
		export_path = str (normpath (join (
			the_exports_path, 
			version,
			database_name, 
			name
		)))
		if (os.path.exists (export_path) != True):
			not_found.append (export_path)
			continue;
		
		script = [
			"mongoimport",
			"--uri",
			URL,
			f"--db={ database_name }",
			f"--collection={ collection_name }",
			f"--file={ export_path }"
		]
		if (drop):
			script.append ('--drop')
		
		print ()
		print ("script:", script)
		procedure.go (
			script = script
		)
		
		time.sleep (.25)
	
	rich.print_json (data = {
		"not found": not_found
	})	
	
	
