import ProjectParser
import VersionParser 
import VersionUpdater 
import glob
import optparse
import subprocess
import sys
import re

from tools.environment.qate import get_solution_list

# Snapshot mode will tag all binaries and create a global tag QATE_{major}.{minor}.{patch}
# target version is either +N or hardcoded version
# dry_run is boolean to allow not actual tagging
# type is 'major' || 'minor' || 'patch'
def UpdateTagSnapshot(target_version, dry_run, force, type):
	if target_version and type != 'show':
		new_version = None
		if target_version.startswith('+'):
			if not target_version[1:].isdigit():
				print 'Error unknown version accumulator' + target_version[1:] 
				return

			current_version = VersionUpdater.GetLatestTaggedVersion('QATE')
			git_version_match = VersionParser.ExtractVersionFromString(current_version) 
			version_parts = git_version_match.group(0).split('.')
			major = version_parts[0]
			minor = version_parts[1]
			patch = version_parts[2]

			incrementValue = int(target_version[1:])
			if type == 'major':
				major = str(int(major) + incrementValue) 
				minor = '0'
				patch = '0'
			elif type == 'minor':
				minor = str(int(minor) + incrementValue) 
				patch = '0'
			elif type == 'patch':
				patch = str(int(patch) + incrementValue) 
			else:
				print 'Error unknown version type ' + type 
				return
			new_version = major + '.' + minor + '.' + patch
		else:
			new_version = target_version
		for project in get_solution_list():
			# Creates local tags for all projects
			Tag(project, new_version, dry_run, force, False)
		Tag('QATE', new_version, dry_run, force, True) 
	else:
		for project in get_solution_list():
			current_version = VersionUpdater.GetLatestTaggedVersion(project, True)
			print "Project {0}: version {1}".format(project, current_version)
		current_version = VersionUpdater.GetLatestTaggedVersion('QATE', True)
		print "Project {0}: version {1}".format('QATE', current_version)

def UpdateTag(project_name, target_version, dry_run, force):
	if target_version:
		new_version = None
		if target_version.startswith('+'):
			current_version = VersionUpdater.GetLatestTaggedVersion(project_name)
			git_version_match = VersionParser.ExtractVersionFromString(current_version)
			new_version_left = git_version_match.group(0).rpartition('.')[0]
			new_version_minor = git_version_match.group(0).rpartition('.')[2]
			current_hotfix_version = 'a'
			if not new_version_minor.isdigit():
				index_postfix = re.search("[^0-9]", new_version_minor).start() 
				new_version_minor_num = new_version_minor[0:index_postfix] 
				current_hotfix_version = new_version_minor[index_postfix] 
				current_hotfix_version = chr(ord(current_hotfix_version) + 1) 
				new_version_minor = new_version_minor_num
			if target_version[1:].isdigit():
				new_version = new_version_left + '.' + str(int(new_version_minor) + int(target_version[1:]))
			elif target_version[1:] == 'hotfix':
				new_version = new_version left + '.' + new_version_minor + current_hotfix_version
			else:
				print 'Error unknown version accumulator' + target_version[1:] 
				return 1
		else:
		   new_version = target_version

		return Tag(project_name, new_version, dry_run, force)
	else:
		current_version = VersionUpdater.GetLatestTaggedVersion(project_name) 
		print "Project {0}: version {1}".format(project_name, current_version)
		return 0

		
def Tag(project_name, version, dry_run, retag, push_tags = True):
	if retag:
		push_tags = True # we need to push
	comment = "[tags][{0}] {1} {0} {2}".format(project_name, "tagging" if not retag else "re-tagging", version)
	git_delete_tag_command_line = ["git", "tag", "-d", "{0}_{1}".format(project_name, version)]
	git_create_tag_command_line = ["git", "tag", "{0}_{1}".format(project_name, version),"-m \"{0}\"".format(comment)]

	git_push_create_tag = ["git", "push", "origin", "--tags"]
	git_push_delete_tag = ["git", "push", "origin", ":refs/tags/{0}_{1}".format(project_name, version)]

	if dry_run:
		if retag:
			print " ".join(git_delete_tag_command_line) 
			print " ".join(git_push_delete_tag)
		print " ".join(git_create_tag_command_line)
		if push_tags:
			print " ".join(git_push create tag) 
		return 0
	else:
		retCode = 0
		if retag:
			subprocess.check_call(git_delete_tag_command_line)
			subprocess.check_call(git_push_delete_tag)
		retCode = subprocess.check_call(git_create_tag_command_line)
		if push_tags:
			retCode = subprocess.check_call(git_push_create_tag)
		return retCode

def newgen_tag(options):
	UpdateTagSnapshot(options.target_version, options.dry_run, options.force, options.increment_type)
	sys.exit(0)



if __name__ == "__main__":
	usage = "%prog [solution xml|UI] [x.y.z] --dry-run --force\nNew gen:\n%prog -n|--newgen -t|--increment_type ['show'|'major'|'minor'|'patch'] -v1--version +1|4.1.2"
	parser = optparse.OptionParser(usage)
	parser.add_option("--dry-run", dest="dry_run", default=False, action="store_true")
	parser.add_option("--force", dest="force", default=False, action="store_true")
	# New gen options
	## This should be updated and defaulted to true once we migrate to new delivery mode everywhere
	## New gen verions are Major.Minor.Patch starting from 4.0.0
	parser.add_option('-n', '--newgen', dest='newgen', action=istore_true', default=False)
	parser.add_option('-t', '--increment-type', dest='increment_type', choices=['show', 'major', 'minor', 'patch'], default = 'minor')  
	parser.add_option('-v', '--version', dest='target_version', default='+1')

	(options, args) = parser.parse_args() 
	if options.newgen:
		newgen_tag(options)
		sys.exit(0)

	if len(args) < 1:
		parser.error("Missing required argument.") 
	version = args[1] if len(args) >= 2 else None
	if (version and not (version.startswith('+') or version.count('.') == 2)): 
		parser.error("{0} not in the format x.y.z or +x".format(version)) 
	retCode = 0

	project_name = None
	project_version_file = None
	if args[0] == "UI":
		try:
			retCode = UpdateTag("UI", version, options.dry_run, options.force) 
		except Exception as e:
			print "Error while updating version and tag for UI: {0}".format(str(e)) 
			retCode = 1
	else:
		for project_filename in glob.glob(args[0]):
			try:
				solution = ProjectParser.ParseSolutionAndProjects(project_filename)
				for project in solution.Targets.values():
					retCode = UpdateTag(project.Name, version, options.dry_run, options.force) 
			except Exception as e:
				print "Error while updating version and tag for file {0}: {1}".format(project_filename, str(e))
				retCode = 1
	sys.exit(retCode)
