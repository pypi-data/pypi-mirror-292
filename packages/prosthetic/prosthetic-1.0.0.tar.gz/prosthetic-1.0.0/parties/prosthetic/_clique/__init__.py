




#from .group import clique as clique_group







#/
#
import prosthetic
import prosthetic.modules.moves.save as save
#
from prosthetic.frontiers.ventures import retrieve_ventures
from prosthetic.frontiers.treasures._clique import treasures_clique
from prosthetic.frontiers.trends._clique import trends_clique
#
from prosthetic._essence import build_essence, retrieve_essence
#
from prosthetic.frontiers.trends.monetary.DB_prosthetic_trends.collection_vernacular._indexes import prepare_collection_vernacular_indexes
#
#
import somatic
from ventures.clique import ventures_clique
#
#
import click
import rich
#
#\

def clique ():
	build_essence ({
		"name": "essence_prosthetic.py"
	})
	'''
		This configures the prosthetic module.
	'''
	#prosthetic.start ()

	print ("starting the prosthetic click.");

	@click.group ()
	def group ():
		pass
		
	@group.command ("form")
	def command_form ():
		prepare_collection_vernacular_indexes ()
	
	@group.command ("school")
	def controls ():
		import pathlib
		from os.path import dirname, join, normpath
		this_directory = pathlib.Path (__file__).parent.resolve ()
		this_module = str (normpath (join (this_directory, "../..")))

		
		somatic.start ({
			"directory": this_module,
			"extension": ".s.HTML",
			"relative path": this_module
		})
		
		import time
		while True:
			time.sleep (1)

	@group.command ("show-essence")
	def controls ():
		essence = retrieve_essence ()
		
		rich.print_json (data = essence)



	group.add_command (ventures_clique ({
		"ventures": retrieve_ventures ()
	}))

	group.add_command (treasures_clique ())
	#group.add_command (mints_clique ())

	#group.add_command (clique_treasures ())
	group.add_command (trends_clique ())
	
	#group.add_command (trends_group.add ())
	
	group ()




#
