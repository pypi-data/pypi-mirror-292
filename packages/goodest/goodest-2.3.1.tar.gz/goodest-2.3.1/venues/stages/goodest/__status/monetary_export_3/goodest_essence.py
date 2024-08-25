





'''
	goodest_1 on --essence-path essence.py
'''

'''
	# near 
	# vicinity
	# not-distant
'''	

'''
	/goodest_frame
		/monetary
			/_data
			
			the.process_identity_number
			the.logs
		
		/harbor
			the.process_identity_number
'''



import json
fp = open ("/online/locker/vaccines_goodest_pypi/treasures/keys_of_OS.1/ellipsis.JSON", "r")
ellipsis = json.loads (fp.read ())
fp.close ()

def crate (the_path):
	from os.path import dirname, join, normpath
	import sys
	import pathlib
	import os
	
	this_directory = pathlib.Path (__file__).parent.resolve ()	
	return str (normpath (join (this_directory, the_path)))


def build ():
	return "built"

essence = {
	
	#
	#	
	#
	"mode": "nurture",
	#"mode": "business",
	
	#
	#	
	#
	"alert_level": "caution",
	
	"ventures": {
		"path": crate (
			"[records]/ventures_map.JSON"
		)
	},
	
	"monetary": {
		"URL": "mongodb://0.0.0.0:39000/",
		#"URL": ellipsis ["monetary"] ["URL"]		
	},
	"sanique": {
		"protected_address_key": "1234"
	},
	"USDA": {
		"food": ellipsis ["USDA"] ["food"]
	},
	"NIH": {
		"supp": ellipsis ["NIH"] ["supp"]
	}
}

onsite = "yes"
if (onsite == "yes"):
	essence ["monetary"] ["onsite"] = {
		"host": "0.0.0.0",
		"port": "39000",
		
		"path": crate (
			"[records]/[monetary_grove]/_data"
		),
		"PID_path": crate (
			"[records]/[monetary_grove]/the.process_identity_number"
		),
		"logs_path": crate (
			"[records]/[monetary_grove]/logs/the.logs"
		)
	}
