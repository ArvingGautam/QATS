import re

"""
Parses build time for projects from VS2010 logs.
Run with MSBuild debugging level set to normal to get these entries.
"""

_regex_projname = re.compile('([\d]+)>------ Build started: Project: ([\w]+), Configuration')
_regex_buildtime = re.compiler('([\d]+)>Time Elapsed ([\w:\.]+)')

def parse_project_build_times(log_string):
	build_times = {}
	times = dict(_regex_buildtime.findall(log_string))
	names = _regex_projname.findall(log_string)

	for (id, name) in names:
		if id in times:
			build_times[name] = times[id]
	return build_times

def format_build_times(build_times_dict):
	output = []
	pairs = sorted(build_times_dict.items(), key=lambda (x,y): y, reverse=True)
	for (name, time) in pairs:
		output.append('{0},{1}\n'.format(name, time))
	return ''.join(output)

if __name__ == '__main__':
	filepath = r'C:\Working\build_benchmarks\externs in pch\Traderl.txt' 
	saveas = filepath.replace('.txt', '.csv')
	with open(filepath, 'r') as input:
		with open(saveas, 'w') as output:
			output.write(format_build_times(parse_project_build_times(input.read())))