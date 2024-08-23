





#/
#
from prosthetic.frontiers.trends.monetary.DB_prosthetic_trends.collection_vernacular.document.insert import insert_document
from prosthetic.frontiers.trends.monetary.DB_prosthetic_trends.collection_vernacular.document.search import search_trends_vernacular
from prosthetic.frontiers.trends.monetary.DB_prosthetic_trends.collection_vernacular.document.count import count_treasures
#
from prosthetic.frontiers.trends.quests.saves._clique import saves_clique
#
#
import click
#
#
import ast
from pprint import pprint
#
#\

def trends_clique ():
	@click.group ("trends")
	def group ():
		pass
	
	
	
	''''
		prosthetic trends insert-document --domain "wallet.1" --names "[ 'name_1', 'name_2' ]"
		prosthetic_1 trends insert-document --domain "wallet.1" --names "[ 'name_1', 'name_2' ]" --topics "[ 'aptos' ]" 
		prosthetic_1 trends insert-document --domain "solid_food.1" --topics "[ 'food' ]" --cautions "[ 'homo-sapiens ages months 6+' ]"
	"'''
	''''
		domain:
			This is unique.
	
		topics:
			This is like similar concepts to the trend.
			
		names:
			This is like synonyms.
			
		cautions:
			This is cautions.
	"'''
	@group.command ("insert-document")
	@click.option ('--names', default = '[]')
	@click.option ('--topics', default = '[]')	
	@click.option ('--cautions', default = '[]')
	def command_insert_document (names, topics, cautions):	
		insert_document ({
			"document": {
				"names": ast.literal_eval (names),
				"topics": ast.literal_eval (topics),
				"cautions": ast.literal_eval (cautions)
			}
		})
	

		
	
	
	
	''''
		prosthetic_1 trends search --names "wallet"
	"'''
	@group.command ("search")
	@click.option ('--name', default = '')
	def command_search (name):
		treasures = search_trends_vernacular ({
			"filter": {
				"names": {
					"$in": [ name ]
				}
			}
		})
		for treasure in treasures:
			pprint (treasure, indent = 4)
			
	@group.command ("count")
	def command_count ():
		count = count_treasures ()
		print ("count:", count)
		
	@group.command ("itemize")
	def command_itemize ():
		treasures = search_trends_vernacular ({
			"filter": {}
		})
		for treasure in treasures:
			pprint (treasure, indent = 4)
		

	group.add_command (saves_clique ())


	return group




#



