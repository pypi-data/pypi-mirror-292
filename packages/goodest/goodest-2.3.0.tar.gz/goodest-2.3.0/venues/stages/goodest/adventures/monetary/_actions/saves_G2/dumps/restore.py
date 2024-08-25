#----
#
from goodest._essence import retrieve_essence
import goodest.mixes.procedure as procedure
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
import json
#
#----


def scan_record (path):
	with open (path, 'r') as FP:
		record = json.load (FP)

	return record

def restore_node (packet):
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
	the_dumps_path = essence ["monetary"] ["saves_G2"] ["dumps"] ["path"]
	URL = essence ["monetary"] ["URL"]
	
	##
	#
	#	calculated
	#
	#
	record_path = str (normpath (join (
		the_dumps_path, 
		version,
		"Node.JSON"
	)))
	collections_record = scan_record (record_path)
	collections = collections_record ["collections"]
	rich.print_json (data = {
		"record_path": record_path,
		"collections_record": collections_record
	})
	
	
	#
	#
	#	Check if that version exists
	#
	#
	version_path = str (normpath (join (
		the_dumps_path, 
		version
	)))
	if (os.path.exists (version_path) != True):
		rich.print_json (data = {
			"does not exist": version_path
		})	
		return;
	
	
	
	not_found = []
	for collection in collections:
		[ database_name, collection_name ] = collection
		
		name = collection_name
		dump_path = str (normpath (join (
			version_path, 
			database_name, 
			name
		)))
		if (os.path.exists (dump_path) != True):
			not_found.append (dump_path)
			continue;
		
		process_strand = [
			"mongorestore",
			"--uri",
			URL,
			f"--db={ database_name }",
			f"--collection={ collection_name }",
			#f"--out={ dump_path }",
			"--gzip",
			f"--archive={ dump_path }"
		]
		if (drop):
			process_strand.append ('--drop')
		
		print ()
		print (" ".join (process_strand))	
		procedure.go (
			script = process_strand
		)
		
		time.sleep (.25)
	
	os.system (f"chmod -R 777 '{ version_path }'")

	rich.print_json (data = {
		"not_found": not_found
	})	
	
	
	return;
	
	
	
	not_possible = []
	for monetary_database in monetary_databases:
		database_name = monetary_databases [ monetary_database ] ["alias"]
		database_collections = monetary_databases [ monetary_database ] ["collections"]
		
		for collection in database_collections:
			dump_name = collection + "." + "dump.gzip"
			dump_path = str (normpath (join (
				the_dumps_path, 
				version,
				database_name, 
				dump_name
			)))
			if (os.path.exists (dump_path) != True):
				not_possible.append (dump_path)
				continue;
				
				
			process_strand = [
				"mongorestore",
				"--uri",
				URL,
				f"--db={ database_name }",
				f"--collection={ collection }",
				#f"--out={ dump_path }",
				"--gzip",
				f"--archive={ dump_path }"
			]
			if (drop):
				process_strand.append ('--drop')
			
			print (" ".join (process_strand))
			
			procedure.go (
				script = process_strand
			)
			
			time.sleep (.25)
	
	os.system (f"chmod -R 777 '{ the_dumps_path }'")

	rich.print_json (data = {
		"not_possible": not_possible
	})	