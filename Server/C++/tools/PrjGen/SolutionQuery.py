# Quick hack so python theo module builder can use correct RV include directory

import sys
import ProjectParser 
import re

argc = len(sys.argv)

if not 4 <= argc <= 5:
	print "Usage: SolutionQuery $ATE_DEV_ROOT solution external [filter_regexp]" 
	print "   e.g. SolutionQuery /home/ammbld/nightly_testrun/ Trader-JP RV Includes" 
	exit (1)

dev_root = sys.argv[1] + '/'
solution = sys.argv[2] 
external = sys.argv[3]

if argc == 5:
	def out(s):
		if re.match(sys.argv[4], s):
			print s
else:
	def out(s):
		print s

solution_xml = dev_root + 'ate/' + solution + '.xml'
os_xml = dev_root + 'ate/Externals_Linux.xml'

xs = ProjectParser.ParseSolutionAndProjects(solution_xml) 

x = xs.Externals[external]

out('Root ' + x.Root)
for b in x.Builds.keys():
	out('Builds.' + b + '.DLLPath ' + str(x.Builds[b].DLLPath))
	out('Builds.' + b + '.DLLs ' + str(x.Builds[b].DLLs))
	for l in x.Builds[b].LibPath:
		out('Builds.' + b + '.LibPath ' + l)
	for l in x.Builds[b].Libs:
		out('Builds.' + b + '.Libs' + ' ' + l)
	out('Builds.' + b + '.Name ' + x.Builds[b].Name)
for d in x.Defines: 
	out('Define ' + repr(d))
out('Version ' + str(x.Version))
out('Name ' + x.Name) 
for d in x.Includes:
	out('Includes ' + str(d))
