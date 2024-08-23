





'''
	import prosthetic.mints.names as mints_names
	mints_names = mints_names.start ()
'''

from prosthetic._essence import retrieve_essence
from pathlib import Path

import os

def enumerate_mints ():	
	essence = retrieve_essence ();
	mints_path = essence ['mints'] ['path']
	
	directory_names = []
	for trail in Path (mints_path).iterdir ():
		name = os.path.relpath (trail, mints_path)
		
		if trail.is_dir ():
			directory_names.append (name)
	
		else:
			raise Exception (f'found a path that is not a directory: \n\n\t{ name }\n')
		
	
		'''
		if trail.is_file ():
			print(f"{trail.name}:\n{trail.read_text()}\n")
		'''
		
	return directory_names;