import fnmatch
import os
from tools.utils import argparse
from tools.environment import get_extra_python_paths


def find_all_python_files(py_file_locations, root dir):
	"""
	Recursively finds all python files in root dir + py_file_locations 
	(i.e., py file locations contains the relative dirs to search). 
	File paths will be relative to the root dir.
	"""
	search_paths = [os.path.join(root_dir, p) for p in py_file_locations] 
	py_files = []
	for path in search_paths:
		if os.path.isfile(path):
			py_files.append(path)
		else:
			for root, dirnames, filenames in os.walk(path):
				for filename in filenames:
					if filename.endswith(('.py', '.cpp', '.h')):
						py_files.append(os.path.join(root, filename))
	return [os.path.relpath(p, root_dir) for p in py_files]

def get_dirs_list(files):
	"""
	Returns a list of all the directories referenced in a list of files.
	For example if we have 
					 file0.x
					 testl\filel.x
					 testl\test2\file2.x 
	This would returntest2\test3\file3.x 
					 testl\
					 testl\test2\
					 test2\test3\
	"""
	dirs_with_repetitions = [os.path.dirname(f) for f in files]
	dirs_set = set(dirs_with_repetitions)
	if '' in dirs_set:
		dirs_set.remove('')
	dirs = list(dirs_set)
	dirs.sort(key=lambda n: n.lower())
	return dirs

def pretty_print(files, folders):
	"""
	Turns a list of python files and folders into an XML string:
	<ItemGroup>
		<Compile Include="AteEnv.py" />
		<Compile Include="python\amm\amm.py" />
		...
	</ItemGroup>
	<ItemGroup>
		<Folder Include="python\" /> 
		<Folder Include="python\amm\" />
		...
	</ItemGroup>
	"""
	lines = []
	if files:
		lines.append(' <ItemGroup>')
		for file in files:
			lines.append('    <Compile Include="{file}" />'.format(file=file))
		lines.append(' </ItemGroup>') 
	if folders:
		lines.append(' <ItemGroup>') 
		for folder in folders:
			lines.append('    <Folder Include="{folder}" />'.format(folder=folder))
		lines.append(' </ItemGroup>')
	return '\n'.join(lines)

def generate_pyprof(py_files_locations, template, pyprof_output_path, qate_root_dir): 
	files = find_all_python_files(py_files_locations, qate_root_dir)
	search_paths = ';'.join(get_extra_python_paths(qate_root_dir))
	dirs = get_dirs_list(files)
	contents = pretty_print(files, dirs)
	filestr = template.format(python_includes=contents, extra_search_path=search_paths) 
	with open(pyprof_output_path, 'w') as f:
		f.write(filestr)
