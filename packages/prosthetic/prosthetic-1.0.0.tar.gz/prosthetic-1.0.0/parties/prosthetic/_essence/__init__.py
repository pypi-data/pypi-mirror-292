

''''
	from prosthetic._essence import build_essence
	build_essence ({
		"name": "essence_prosthetic.py"
	})
"'''

''''
	#
	#	From sanic this is necessary
	#
	#
	from prosthetic._essence import build_essence
	build_essence ({
		"path": ""
	})
"'''

''''
	from prosthetic._essence import retrieve_essence
	essence = retrieve_essence ()
"'''

#/
#
from .behavior.seek import seek_essence
from .behavior.scan import scan_essence
from .behavior.merge import merge_essence
from .behavior.form import form_essence
#
from .prefab import retrieve_prefab
#
#
import rich
import pydash
#
#
import pathlib
from os.path import dirname, join, normpath
import sys
import os
#
#\

essence = {}
essence_built = "no"
essence_name = "essence_prosthetic.py"

def build_essence (packet = {}):
	global essence_built;
	global essence;	
	if (essence_built == "yes"):
		return;
		
	packet ["name"] = essence_name;
	packet ["retrieve_prefab"] = retrieve_prefab

	essence = form_essence (packet)
	essence_built = "yes"
	
	return;

''''
def build_essence_v1 (* positionals):
	global essence_built;
	if (essence_built == "yes"):
		return;
	
	essence_path = ""
	if (len (positionals) >= 1):
		if ("essence_path" in positionals [0]):
			essence_path = positionals [0] ["essence_path"]

	if (len (essence_path) == 0):
		essence_path = seek_essence ({
			"name": "essence_prosthetic.py"
		})
	
	external_essence = scan_essence (essence_path)
	internal_essence = merge_essence (
		retrieve_prefab ({
			"essence_path": essence_path
		}),
		external_essence
	)
	for key in internal_essence:
		essence [ key ] = internal_essence [key]

	essence_built = "yes"

	return;
"'''

#
#	Use this; that way can easily
# 	start using redis or something.
#
def retrieve_essence ():
	build_essence ()
	return essence


