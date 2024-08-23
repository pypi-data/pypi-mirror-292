
from ..seek import seek_essence
from ..scan import scan_essence
from ..merge import merge_essence

def form_essence (packet):
	essence_path = ""
	if ("path" in packet):
		essence_path = packet ["path"]
	elif ("name" in packet):
		essence_path = seek_essence ({
			"name": packet ["name"]
		})
	
	
	
	essence = {}
	
	print ("essence_path:", essence_path, packet)
	
	external_essence = scan_essence (essence_path)
	merged_essence = merge_essence (
		packet ["retrieve_prefab"] ({
			"essence_path": essence_path
		}),
		external_essence
	)
	#for key in internal_essence:
	#	essence [ key ] = internal_essence [key]
	
	return merged_essence;