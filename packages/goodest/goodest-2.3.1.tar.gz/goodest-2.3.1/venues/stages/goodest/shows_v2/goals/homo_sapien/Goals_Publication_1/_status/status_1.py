

''''
	python3 status.proc.py shows_v2/goals/homo_sapien/Goals_Publication_1/_status/status_1.py
"'''

from goodest.shows_v2.goals.homo_sapien.Goals_Publication_1 import build_Goals_Publication_1
	

def etch (bracket, name):
	import pathlib
	from os.path import dirname, join, normpath
	this_directory = pathlib.Path (__file__).parent.resolve ()
	the_path = normpath (join (this_directory, name))

	from goodest.mixes.drives.etch.bracket import etch_bracket
	etch_bracket (the_path, bracket)
		
	

def check_1 ():
	goals = build_Goals_Publication_1 ()
	
	etch (goals, "goals.JSON")
	
	assert ("label" in goals)
	assert ("cautions" in goals)
	assert ("qualities" in goals)
	assert ("recipe" in goals)
	assert ("essential nutrients" in goals ["recipe"])

	assert (len (goals ["qualities"]) == 35), len (goals ["qualities"])
	
	return;
	
	
checks = {
	'check 1': check_1
}