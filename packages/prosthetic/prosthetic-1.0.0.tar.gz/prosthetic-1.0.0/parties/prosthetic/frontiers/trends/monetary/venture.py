


'''
	from prosthetic.frontiers.trends.monetary.venture import trends_monetary_venture
	trends_monetary_venture ()
'''

from ._controls.on import turn_on_monetary_node
from ._controls.off import turn_off_monetary_node
from ._controls.status import check_monetary_status

def trends_monetary_venture ():
	return {
		"name": "trends monetary",
		"kind": "task",
		"turn on": {
			"adventure": turn_on_monetary_node,
		},
		"turn off": turn_off_monetary_node,
		"is on": check_monetary_status
	}