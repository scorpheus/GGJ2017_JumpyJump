import sys
from cx_Freeze import setup, Executable


# Gather extra runtime dependencies.
def gather_extra_redist():
	import os
	import gs
	import inspect

	path = os.path.dirname(inspect.getfile(gs))
	files = os.listdir(path)

	out = []
	for file in files:
		name, ext = os.path.splitext(file)
		if ext in ['.dll', '.so'] and "Debug" not in name:
			out.append(os.path.join(path, file))

	return out


extra_redist = gather_extra_redist()

includes      = []
include_files = ["assets", "C:\\Anaconda3\\Lib\\site-packages\\numpy", "C:\\Anaconda3\\Lib\\site-packages\\scipy"] + extra_redist

# Dependencies are automatically detected, but it might need fine tuning.
options = {
	'build_exe': {
		'build_exe': './build',
		'no_compress': False,
		'packages': ['gs'],
		"includes": includes,
		"include_files": include_files
	}
}

setup(  name = "JumpyJump",
		version = "1.0",
		description = "GGJ2017",
		options = options,
		executables = [Executable("jumpyjump.py")])
