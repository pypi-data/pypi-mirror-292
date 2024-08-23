
#/
#
from ._quests.itemize import itemize_treasures
from ._quests.pass_treasure import pass_treasure
#
#
import click
#
#
import os
#
#\

def treasures_clique ():
	@click.group ("treasures")
	def group ():
		pass
		
		
	@group.command ("itemize")
	def command_itemize ():		
		itemize_treasures ({
			"print_to_shell": "yes"
		})
		
		
		
	''''
		prosthetic_1 treasures pass --domain "health.1" --path "./health.1" --version freshest
	"'''
	''''
		"directories": {
			"freshest": ""
		} 
	"'''
	@group.command ("pass", help = """
		
		This is for passing a treasure to the trends.
		
	""")
	@click.option ('--domain', required = True)
	@click.option ('--path', required = True)
	@click.option ('--version', default = 'freshest')
	def command_insert_directory (domain, path, version):
		CWD = os.getcwd ()
	
		#
		#	moves:
		#		1. tar the treasure with "ships"
		#
		print ("command_insert_directory")
		
		pass_treasure ({
			"domain": domain,
			"path": path,
			"version": version
		})
		
		return;

	return group




#



