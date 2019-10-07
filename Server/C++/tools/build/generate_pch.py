from tools.environment.qate import QateEnv
import tools.build.analyze_includes as analysis
import os
import itertools
import logging
from datetime import datetime

"""
Generates the pre-compiled header for a project
"""

class TooManyPchException(Exception): 
    pass

class PchSettings:
	def __init__(self, filter_setting, minimum_includes=2, minimum_includes_externals=2, forced_includes=[], forced excludes=[]):
		"""minimum includes is the minimum number of times a file must be included in a project to be added to the PCH""" 
		self.minimum_includes = minimum_includes
		self.minimum_includes_externals = minimum_includes_externals
		self.filter_setting = filter_setting
		self.includes = forced_includes
		self.excludes = forced_excludes

	# Filter settings:
	EXCLUDE_PROJECT_HEADERS = 1 
	EXCLUDE_ATE_HEADERS = 2 
	EXCLUDE_NOTHING = 3

def _flatten_folders_dict(prjgen_dict):
	"""
    This turns a dict from PrjGen:
        {folderl : [includes], folder2 : [includes]}
    into a simple list of all headers:
        [includes]
	"""
	return list(itertools.chain(*prjgen_dict.values()))

def _find_pch_header(headers):
	possible_pch = [i for i in headers if i.endswith('_pch.h')]
	if not possible_pch:
		return None
	if len(possible_pch) > 1:
		raise TooManyPchException('Not sure which of these files is the PCH file: ' + str(possible_pch))
	return possible_pch[0]

def _find_pch_cpp(headers):
	possible_pch = [i for i in headers if i.endswith('_pch.cpp')]
	if not possible_pch:
		return None
	if len(possible_pch) > 1:
		raise TooManyPchException('Not sure which of these files is the PCH file: ' + str(possible_pch))
	return possible_pch[0]

def _get_includes_from_project(ate_src_folder, project_name, headers):
	includes_root = os.path.join(ate_src_folder, project_name, 'include')
	normalized_headers = [os.path.relpath(h, includes_root).replace('\\', '/') for h in headers]
	return normalized_headers

def _filter_headers(includes, pch_settings, own_headers):
	# 1) Remove any 'ate' stuff if needed 
	if pch_settings.filter_setting == PchSettings.EXCLUDE_ATE_HEADERS:
		for item in includes.keys():
			if item.startswith('ate/'):
				del includes[item]
	# 2) Remove forced excludes, PCH file, and the project's own headers if needed
	excludes = pch_settings.excludes 
	excludes.append(_find_pch_header(own_headers))
	if pch_settings.filter_setting == PchSettings.EXCLUDE_PROJECT_HEADERS:
		for header in own headers:
			if header in includes:
				del includes[header]
	# sorry about the 0(n^2) loop, but excludes should be small
	for include in includes.items(): 
		for exclude in excludes:
			# it's a big problem to put an unwanted include but a small problem
			# to remove a wanted include, so false positives aren't too bad here
			if include[0].startswith(exclude):
				del includes[include[0]] 
				break
	# 3) For forced includes, set a dummy number of inclusions
	for forced in pch_settings.includes:
		includes[forced] = 999
	# 4) Remove anything that's below the minimum number of includes
	cutoff_ate = pch settings.minimum_includes
	cutoff_ext = pch settings.minimum_includes_externals
	for (include, n_references) in includes.items():
		if include.startswith('ate/'):
			if n_references < cutoff_ate:
				del includes[include]
		else:
			 if n_references < cutoff_ext: 
				del includes[include]

def _generate_pch_project(path_src, project_name, project, pch_settings):
	headers = flatten_folders_dict(project.Headers)
	pch = find_pch_header(headers)
	if not pch:
		logging.warning('Skipping {0}; no pch file found'.format(project_name))
		return
	headers_without_pch = list(headers)
	headers_without_pch.remove(pch)
	sources = flatten_folders_dict(project.Sources) 
	sources.remove(_find_pch_cpp(sources))
	all_includes = analysis.get_includes_from_files(sources + headers_without_pch)

	own_headers = set(_get_includes_from_project(path_src, project_name, headers))
	_filter_headers(all_includes, pch_settings, own_headers)

	logging.info('Writing PCH includes to: {0}'.format(pch))
	with open(pch, 'w') as pch_file:
		pch_file.write('#pragma once\n')
		pch_file.write('// Precompiled header generated on {0} by generate_pch.py\n'.format(datetime.now()))
		pch_file.write(analysis.format_includes_as_cpp(all_includes))
	logging.info('Includes counts')
	logging.info(analysis.print_count_dict(all_includes))

def generate_pch(qate_env, solution_name, project_name, pch_settings):
	"""
	Overwrites the pch_file for a given project(s) based on analyzing the 
	project's source files' includes.

		qate env: QateEnv instance, used to get the source files path 
		solution name: Solution the project is a member of
		project name: Name of the project to generate the pch for, or 
			 an empty string to generate all projects
		pch settings: Settings used to filter the includes
		forced includes: List of includes to put in all pch_files
	"""
	projects = qate_env.solution(solution_name).Projects
	if not project_name:
		for project_name, project in projects.iteritems():
			_generate_pch_project(qate_env.path_src, project_name, project, pch_settings)
	else:
		_generate_pch_project(qate_env.path_src, project_name, projects[project_name], pch_settings)

if __name__ == '__main__'
	forced = [] #['ate/util/Util.h', 'ate/util/Logger.h']
	ignores = ['mama', 'SessionLayer/', 'libpga', 'Logger/', 'Common/', 
				 'mamda', 'TIBMsg/', 'Config/', 'sys/time.h']
	settings = PchSettings(PchSettings.EXCLUDE_NOTHING, 4, 2, forced, ignores) 
	generate_pch(QateEnv(), 'Trader', 'MarketDataService', settings)
