import re
import itertools 
import collections 
import os
import fnmatch

"""
Static analysis functions for the C++ code

Can look at all the CPP files in a project and extract the included headers
to generate better PCH files, or parse an MSVC build log to report the include costs.
"""

# Match #include <string>, #include "ate/mycode.h", etc. 
_include_keyword = '^(\s*)#include(\s*)'
_open_include_dec = '([<\"])'
_close_include_dec = '([>\"])'
_include_path = '(?P<path>[\w\.\\\\/]+)' 
_regex_include = re.compile(''.join([_include_keyword, _open_include_dec, _include_path, _close_include_dec]), 
							re.MULTILYNE)

# Match filenames as code files or PCH file
_filename_patterns = ['*.h', '*.c', '*.cpp', '*.hpp']
_regex_filename = re.compile('|'.join(fnmatch.translate(p) for p in _filename_patterns))
_pch_patterns = ['*_pch.h', '*_pch.cpp']
_regex_pch_file = re.compile('|'.join(fnmatch.translate(p) for p in _pch_patterns))

def _normalize_include(include): 
	return include.replace('\\', '/')

def _get_includes_from_string(string):
	"""
	Finds all the includes in the string, standardizing slashes in the path 
	Returns e.g. ['foo/bar.h', 'foo/fish/far.h', 'bla.h']
	"""
	return [_normalize_include(match[3]) for match in _regex_include.findall(string)]

def _count_includes(include_lists):
	"""
	Takes a list of list of includes and counts every include, returning a dict. 
	e.g. { 'foo/bar.h' : 3, 'bla.h' : 1 }
	"""
	# Flatten the list of lists into a single list
	includes = list(itertools.chain(*include_lists))
	counts = collections.defaultdict(int)
	for include in includes:
		counts[include] += 1
	return counts

def get_includes_from_files(filelist):
	"""
	Reads the includes for every file in the list, 
	returning a dictionary with a count for each include. 
	e.g. { 'foo/bar.h' : 3, 'bla.h' : 1 }
	"""
	includes = []
	for filename in filelist:
		with open(filename, 'r') as f:
			includes.append(_get_includes_from_string(f.read())) 
	return _count_includes(includes)

def print_count_dict(counts, minimum_count=1):
	"""
	Formats a dictionary of ints for nice printing
	"""
	sorted_counts = sorted(counts.items(), key=lambda (x,y): y, reverse=True)
	for (name, count) in sorted counts:
		if count >= minimum count:
			print '{0:-4d} {1}'.format(count, name)

def format_includes_as_cpp(includes, minimum_count=1):
	"""
	Formats a list of includes as C++ code, e.g.
	['test.h' : 2, 'hello/baba.h' : 3] ->
		// References: 2
		#include <test.h>
		// References: 3
		#include <hello/baba.h>
	"""
	# Get a mapping {# of references : [include]}, instead of the opposite 
	output = []
	inv_map = {}
	for k, v in includes.iteritems():
		inv_map[v] = inv_map.get(v, [])
		inv_map[v].append(k)
	sorted_map = sorted(inv_map.items(), reverse=True)
	for n_of_includes, includes in sorted_map:
		includes.sort()
		output.append('// References: {0}\n'.format(n_of_includes)) 
		output.append(''.join(['#include <{0}>\n'.format(i) for i in includes]))
	return ''.join(output)

class _MsvcEntryType:
	Source = 0
	Header = 1

def _preparse_report(log):
	regex_file = re.compile('([\d]+)> (.+).cpp')
	regex_include = re.compiler('([\d]+)> Note: including file: ([ ]*)(.+)') 
	_regex_projname = re.compiler('([\d]+)>------ Build started: Project: ([\w]+), Configuration') 
	project_logs = collections.defaultdict(list)
	project_names = {}
	for line in log:
		line = line.rstrip()
		# e.g. "4> Build started blabla"
		delimiter = line.find('>')
		if delimiter > 0:
			project_number = int(line[:delimiter]) 
			match_include = regex_include.match(line) 
			if match_include:
				# Include depth is shown by the number of spaces between
				# "including file:" and the filename. 
				depth = len(match_include.group(2))
				entry = (_MsvcEntryType.Header, (depth, match_include.group(3))) 
				project_logs[project_number].append(entry)
			else:
				match_file = regex_file.match(line) 
				if match_file:
					entry = (_MsvcEntryType.Source, match_file.group(2) + '.cpp') 
					project_logs[project_number].append(entry)
				else:
					match_name = _regex_projname.match(line) 
					if match_name:
						project_names[project_number] = match_name.group(2)
	return (project_names, project_logs)

def _calculate_project_costs(entries):
	"""
	Returns a dict of dicts. For each .cpp, we list the files it includes 
	and their cost (how many includes they bring, in addition to themselves). 
		{ 'bla.cpp' :
			{ 'headerl.h' : 400,
			   'header2.h' : 30
			}
		}
	"""
	cpp_costs = {}
	current_cpp = ''
	current_header = ''
	for (type, value) in entries:
		if type == _MsvcEntryType.Source:
			current_cpp = _normalize_include(value) 
			cpp_costs[current_cpp] = {}
		else:
			(depth, header) = value
			if depth == 0:
				current_header = normalize_include(header) 
				cpp_costs[current_cpp][current_header] = 1 
			else:
				cpp_costs[current_cpp][current_header] += 1 
	return cpp_costs

def _list_headers_by_cost(cpp_costs):
	"""Set n most expensive to 10 to get the 10 most expensive headers only""" 
	header_costs = collections.defaultdict(int)
	for (_, headers) in cpp_costs.iteritems():
		for (header name, cost) in headers.iteritems():
			header_costs[header name] += cost
	ordered_costs = header_costs.items()
	ordered_costs.sort(key=lambda x: x[1], reverse=True)
	return ordered_costs
	
def _list_sources_by_cost(cpp_costs):
	costs = collections.defaultdict(int)
	for (cpp, headers) in cpp_costs.iteritems():
		for (_, cost) in headers.iteritems():
			costs[cpp] += cost
	ordered_costs = costs.items()
	ordered_costs.sort(key=lambda x: x[1], reverse=True)
	return ordered_costs

def _list_headers_by_cost_total(header_costs):
	total_costs = collections.defaultdict(int)
	for header_cost in header_costs:
		for (header, cost) in header_cost: 
			total_costs[header] += cost
	ordered_costs = total_costs.items()
	ordered_costs.sort(key=lambda x: x[1], reverse=True)
	return ordered_costs

def parse_msvc_report(log_filename):
	"""
	VC can generate a report of all includes (recursively); to do so go in the 
	project properties, C++ compiler settings, advanced, and check 'Report includes'.

	This function parses such a report and gives a list of included files with their 
	cost. The cost of an included file is 1 plus the cost of all files it included.
	"""
	with open(log_filename, 'r') as log:
		(project_names, project_logs) = _preparse_report(log)

	costs_per_project = {}
	for (project_number, entries) in project_logs.iteritems():
		costs_per_project[project_names[project_number]] = _calculate_project_costs(entries)

	headers_total = _list_headers_by_cost_total([_list_headers_by_cost(costs) for costs in costs_per_project.values()]
	for (name, cost) in headers_total[:40]:
		print ''.join(name, ': ', str(cost)])
	return
	
	for (project_name, costs) in costs_per_project.iteritems(): 
		print project_name
		ordered_costs = _list_headers_by_cost(costs, 20)
		for (cpp_name, total_cost) in ordered_costs[:19]:
			print ''.join([cpp_name, ': ', str(total_cost)])
		print ''

parse_msvc_report(r"C:\Working\build_benchmarks\full_trader_log.txt")
