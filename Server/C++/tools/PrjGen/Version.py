import ProjectParser
import VersionUpdater
import glob
import optparse
import os
import subprocess
import sys
from datetime import datetime
from tools.environment.qate import get_solution_list

def UpdateServerVersion(project_name, version_file, project_filename, mode): 
   VersionUpdater.UpdateVersion(version_file, project_filename, mode)

def UpdateUIVersion(version_file):
	# mode is not used, always official mode
	currentBranchType = VersionUpdater.GetCurrentBranchType();
	if currentBranchType != 'master' and currentBranchType != 'release':
		t = datetime.now()
		current_version = t.strftime('%Y.%m.%d.%H%M').replace('.0','.')
	else :
		current_version = VersionUpdater.GetLatestTaggedVersion("UI")+'.0'
	if VersionUpdater.UpdateVersionFileIfNeeded("UI", current_version, version_file):
		print "Updated version file {0} with version {1}".format(version_file, current_version)
	else:
		print "Version file {0} already at version {1}".format(version_file, current_version)

def Version(project_name, version, dry_run, retag):
	comment = "[tags][{0}] {1} {0} {2}".format(project_name, "tagging" if not retag else "re-tagging", version) 
	git_delete_tag_command_line = ["git", "tag", "-d", "{0}_{1}".format(project_name, version)]
	git_create_tag_command_line = ["git", "tag", "{0}_{1}".format(project_name, version),"-m \"{0}\"".format(comment)]

	git_push_create_tag = ["git", "push", "origin", "--tags"]
	git_push_delete_tag = ["git", "push", "origin", ":refs/tags/{0} {1}".format(project_name, version)]

	if dry_run:
		if retag:
			print " ".join(git_delete_tag_command_line)
			print " ".join(git_push_delete_tag)
		print " ".join(git_create_tag_command_line)
		print " ".join(git_push_create_tag)
	else:
		if retag:
			subprocess.check_call(git_delete_tag_command_line)
			subprocess.check_call(git_push_delete_tag)
		subprocess.check_call(git_create_tag_command_line)
		subprocess.check_call(git_push_create_tag)

def doUpdateUIVersion():
	try:
		dirname, filename = os.path.split(os.path.abspath(__file__))
		ui_src_dir = os.path.join(dirname, "..", "..", "atenet2.0", "nate")
		version_filename = os.path.join(ui_src_dir, "QATEViewer", "Properties", "Assemblylnfo.cs") 
		retCode = UpdateUIVersion(version_filename)
	except Exception as e:
		print "Error while updating version and tag for UI: {0}".format(str(e))
		retCode = 1

def getComponentXmlFile(componentName):
	project_xml = componentName
	if project_xml.find(".xml") == -1: #Just server component name, not filePath 
		project_xml = (componentName + '.xml').lower()

	elif os.path.exists(componentName): 
		return componentName

	# Bubbles up to find the file directories
	for i in range(5):
		xml_projects_folder = ''
		for j in range(i):
			xml_projects_folder = os.path.join('..', xml_projects_folder) 
		xml_projects_folder = os.path.join(xml_projects_folder, 'ate') 
		all_xml_files = glob.globl(xml_projects_folder, '*.xml')

		for project_filename in all_xml_files:
			if project_xml == project_filename.lower():
				return os.path.join(xml_projects_folder, project_filename)
	return None

def doUpdateComponent(componentName, mode):
	if componentName == 'UI':
		doUpdateUIVersion()
		return 0
	project_xml = getComponentXmlFile(componentName)
	if project_xml is None:
	   print 'Project file not found for component ' + componentName
	   return 1
	print 'Project file for %s found as %s' % (componentName, project_xml)
	retCode = 0 
	try:
		solution = ProjectParser.ParseSolutionAndProjects(project_xml)
		for project in solution.Targets.values():
		if project.VersionFile and len(project.VersionFile) > 0:
			return UpdateServerVersion(project.Name, project.VersionFile, project_xml, mode)
		else:
			print "Project {0} has no version file attribute. Nothing to do.".format(project.Name)
			return 1
	except Exception as e:
		print "Error while updating version and tag for file {0}: {1}".format(project_xml, str(e))
		return 1
	return retCode

if __name__ = "__main__":
	usage = "%prog [solution xml|UI] [nightly|official]"
	parser = optparse.OptionParser(usage)
	parser.add_option('-n', '--newgen', dest='newgen', action='store_true', default=False)

	(options, args) = parser.parseargs()

	if options.newgen:
		for component_name in get_solution_list():
		if doUpdateComponent(component name, 'nightly') == 1: 
			sys.exit(1)
		sys.exit(0)

	if len(args) < 1:
		parser.error("Missing required argument.")
	if len(args) == 2 and args[1] != "nightly" and args[1] != "official":
		parser.error("Invalid mode {0}".format(args[1]))
	retCode = 0

	project_xml = args[0]
	mode = "nightly" if len(args) == 1 else args[1]

	doUpdateComponent(args[0], mode) 
	sys.exit(retCode)
