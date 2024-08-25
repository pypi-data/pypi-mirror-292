
'''
	def etch (bracket, name):
		import pathlib
		from os.path import dirname, join, normpath
		this_directory = pathlib.Path (__file__).parent.resolve ()
		the_path = normpath (join (this_directory, name))

		from goodest.mixes.drives.etch.bracket import etch_bracket
		etch_bracket (the_path, bracket)
		
	etch ({}, "bracket.JSON")
'''

import pathlib
from os.path import dirname, join, normpath
import json

def etch_bracket (path, data):
	FP = open (path, "w")
	FP.write (json.dumps (data, indent = 4))
	FP.close ()