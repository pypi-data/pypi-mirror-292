
''''
	from prosthetic.frontiers.treasures.check.domain_fiber import check_domain_fiber
	check_domain_fiber ({
		"domain_fiber": ""
	})
"'''

def check_domain_fiber (packet):
	fiber = packet ["domain_fiber"]
	fiber_dot_count = fiber.count (".")
	
	assert (fiber_dot_count == 1), fiber_dot_count
	
	
	
	return;