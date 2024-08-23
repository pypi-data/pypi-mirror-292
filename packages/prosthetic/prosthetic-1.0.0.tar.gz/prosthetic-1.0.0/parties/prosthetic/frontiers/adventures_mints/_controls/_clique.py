


#/
#
from .._quests.enumerate import enumerate_mints
#
#
import click
#
#\

def mints_clique ():
	@click.group ("mints")
	def group ():
		pass


	@group.command ("enumerate")
	def enumerate ():		
		enumerate_mints ()


	return group




#



