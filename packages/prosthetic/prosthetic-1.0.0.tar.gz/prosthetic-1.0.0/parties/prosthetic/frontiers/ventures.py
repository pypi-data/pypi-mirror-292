




'''
	from prosthetic.frontiers.ventures import retrieve_ventures
	ventures = retrieve_ventures ()
'''

#/
#
from .trends.sanique.venture import sanique_venture
from .trends.monetary.venture import trends_monetary_venture
#
#
from prosthetic._essence import retrieve_essence
#
#
from ventures import ventures_map
#
#\

def retrieve_ventures ():
	essence = retrieve_essence ()

	return ventures_map ({
		"map": essence ["ventures"] ["path"],
		"ventures": [
			sanique_venture (),
			trends_monetary_venture ()
		]
	})