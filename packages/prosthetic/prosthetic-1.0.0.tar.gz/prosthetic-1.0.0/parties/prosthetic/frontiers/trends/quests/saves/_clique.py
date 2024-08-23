

#/
#
from .exports.monetary_export import export_documents
from .exports.monetary_import import import_documents
#
from .dumps.dump import dump_node
from .dumps.restore import restore_node
#
from prosthetic._essence import retrieve_essence
import prosthetic.mixes.procedure as procedure
from prosthetic.frontiers.trends.monetary.DB_prosthetic_trends.collection_vernacular._indexes import prepare_collection_vernacular_indexes
	
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
#
#\


def saves_clique ():
	@click.group ("saves")
	def group ():
		pass
	
	
	'''
		mongodump --uri="URL" 
	'''
	@group.command ("dumps-dump")
	@click.option (
		'--version',
		required = True
	)
	def clique_dump (version):	
		dump_node ({
			"version": version
		})
		
	@group.command ("dumps-restore")
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
		itinerary:
			[ ] prosthetic_1 adventures monetary saves export --version 2
					[ ] { database }.{ collection }.{ version }.JSON
	'''
	@group.command ("exports-export")
	@click.option (
		'--version',
		required = True
	)
	def save (version):	
		export_documents ({
			"version": version
		})
	
	'''
		prosthetic_1 adventures monetary saves import --version 2 --drop
	'''
	@group.command ("exports-import-overwrite")
	@click.option ('--version', required = True)
	def insert (version):
		import_documents ({
			"version": version,
			"drop": True			
		})
		
		prepare_collection_vernacular_indexes ()
		
	@group.command ("exports-import-merger")
	@click.option ('--version', required = True)
	def insert (version):
		import_documents ({
			"version": version,
			"drop": False			
		})
		

	return group




#



