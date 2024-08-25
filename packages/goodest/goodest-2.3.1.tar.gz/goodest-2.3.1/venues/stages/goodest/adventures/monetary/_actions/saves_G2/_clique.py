

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
import ast
#
#----

from .exports.monetary_export import export_documents
from .exports.monetary_import import import_documents

from .dumps.dump import dump_node
from .dumps.restore import restore_node

from .saves.save import save_node
from .saves.extract import extract_node


def monetary_saves_clique_G2 ():
	@click.group ("saves-G2")
	def group ():
		pass
	

	@group.command ("save")
	@click.option ('--version', required = True)
	@click.option ('--databases', required = True)
	def clique_dump (version, databases):
		database_names = ast.literal_eval (databases)
		
		save_node ({
			"database_names": database_names,
			"version": version,
			"formats": [ "export", "dump" ]
		})
		
	
	@group.command ("extract")
	@click.option ('--version', required = True)
	def clique_dump (version):
		extract_node ({
			"version": version,
			"format": "export",
			"wipe": "yes"
		})
	
	
	
	#
	#
	#
	#
	#
	#
	#
	
	
	'''
		mongodump --uri="URL" 
	'''
	@group.command ("dump")
	@click.option (
		'--version',
		required = True
	)
	@click.option ('--databases', required = True)
	def clique_dump (version, databases):
		database_names = ast.literal_eval (databases)
		
		dump_node ({
			"database_names": database_names,
			"version": version
		})
		
	@group.command ("restore")
	@click.option (
		'--version',
		required = True
	)
	@click.option (
		'--drop', 
		help = "drop the current documents in the collection", 
		is_flag = True
	)
	def clique_restore (version, drop):	
		restore_node ({
			"version": version,
			"drop": drop
		})	
		
	'''
		TODO:
			export --version 14 --databases '[ "goodest_inventory", "goodest_tract" ]'
	'''
	@group.command ("export")
	@click.option ('--version', required = True)
	@click.option ('--databases', required = True)
	def save (version, databases):
		database_names = ast.literal_eval (databases)

		export_documents ({
			"database_names": database_names,
			"version": version
		})
	
	'''
		goodest_1 adventures monetary saves import --version 2 --drop
	'''
	@group.command ("import")
	@click.option ('--version', required = True)
	@click.option (
		'--drop', 
		help = "drop the current documents in the collection", 
		is_flag = True
	)
	def insert (version, drop):
		import_documents ({
			"version": version,
			"drop": drop			
		})
		

	return group




#



