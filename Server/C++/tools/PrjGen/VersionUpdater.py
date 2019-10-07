import ProjectParser
from VersionParser import ExtractVersion
from VersionParser import ExtractVersionFromString
import optparse
import os
import re
import subprocess
import sys

RE_HEADER_FILENAME = re.compile(r"(.*)(\.h)")
RE_VERSION = re.compile(r"([^\"\.]+\.[^\.]+\.[^\.]+)\.([^-\"]+)(-[a-zA-Z]+)?")

def ExtractRevisionAndURL(iATEFolder, iTargetName):
	revision = ""
	url = ""

	for i in range(1,10):
		version_abbrev_hashes = subprocess.Popen(["git", "log", "--pretty=format:%h", iATEFolder], stdout = subprocess.PIPE).communicate()[0]
		if len(version_abbrev_hashes) == 0 or len(version_abbrev_hashes.split("\n")) == 0:
			continue
		else:
			revision = version_abbrev_hashes.split("\n")[0]
			break
	if len(revision) == 0:
		raise Exception("Unable to get commit logs.")

	for i in range(1,10):
		url = subprocess.Popen(["git", "describe", "--match", "{0}_*".format(iTargetName), "--tags", "--all", "--always"], stdout = subprocess.PIPE).communicate()[0]
		if len(url) == 0:
			continue
		break

	# output when we're at the tag:     Trader_3.5.11
	# output when NOT we're at the tag: Trader_3.5.11-1-g2Oldb48
	if len(url) == 0:
		raise Exception("Unable to get url.")

	return (revision, url)

def CheckAndFlagAsOfficial(iTargetName, iVersion, iATEFolder, iMode):
	version_match = RE_VERSION.match(iVersion)
	if version_match:
		major = version_match.group(1)
		minor = version_match.group(2)
		flag = version_match.group(3)
		(revision, url) = ExtractRevisionAndURL(iATEFolder, iTargetName)
		if ((iMode == "official" and "-" not in url and major in url and "Beta" in flag)):
			return major + '.' +  revision
	return iVersion

def UpdateVersionFileIfNeeded(iProjectName, iNewVersion, iVersionFilename): 
	existing_version_match = ExtractVersion(iVersionFilename)
	new_version_match = ExtractVersionFromString(iNewVersion)
	# TODO: the following condition always returns true for UI because it loads the entire version file
	if (not existing_version_match or
		existing_version_match.group(0) != new_version_match.group(0) or 
		existing_version_match.group(1) != new_version_match.group(1)):

		contents = None
		if iProjectName == "UI":
			contents = """
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using System.Windows.Markup;

// General Information about an assembly is controlled through the following 
// set of attributes. Change these attribute values to modify the information 
// associated with an assembly.
[assembly: AssemblyTitle("QATEViewer")]
[assembly: AssemblyDescription("QATE Trading")] 
[assembly: AssemblyConfiguration("")]
[assembly: AssemblyCompany("Merrill Lynch Inc.")] 
[assembly: AssemblyProduct("QATEViewer")]
[assembly: AssemblyCopyright("Copyright (c) Merrill Lynch Inc. 2008")] 
[assembly: AssemblyTrademark("")]
[assembly: AssemblyCulture("")]
[assembly: log4net.Config.XmlConfigurator(Watch = true)] 
[assembly: InternalsVisibleTo("QATEViewer.Test")]

// Setting ComVisible to false makes the types in this assembly not visible 
// to COM components. If you need to access a type in this assembly from 
// COM, set the ComVisible attribute to true on that type.
[assembly: ComVisible(false)]

// The following GUID is for the ID of the typelib if this project is exposed to COM 
[assembly: Guid("cda45972-a4d5-4c44-a0e3-4eeabe01898b")]

// Version information for an assembly consists of the following four values: 
//
//      Major Version
//      Minor Version
//      Build Number
//      Revision
//
[assembly: AssemblyVersion("{0}")]
[assembly: AssemblyFileVersion("{0}")]

[assembly: InternalsVisibleTo("QATEViewerUnitTest")]
""".format(iNewVersion)
		else:
			contents = "#define ATE_VERSION \"{0}\"".format(iNewVersion)

		open(iVersionFilename, 'w').write(contents)
		return True
    return False

def GetGitRevision(iATEFolder):
	revision = ""
	for i in range(1,10):
		version_abbrev_hashes = subprocess.Popen(["git", "log", "--pretty=format:%h", iATEFolder], stdout = subprocess.PIPE).communicate()[0]
		if len(version_abbrev_hashes) == 0 or len(version_abbrev_hashes.split("\n")) == 0:
			continue
		else:
			revision = version_abbrev_hashes.split("\n")[0]
			break
	if len(revision) == 0:
		raise Exception("Unable to get commit logs.")

	for i in range(1,10):
		status = subprocess.Popen(["git", "status", iATEFolder], stdout = subprocess.PIPE).communicate()[0] 
		if len(status) > 0:
			break
	if len(status) == 0:
		raise Exception("Unable to get git status.")

	revision += "-Alpha" if "modified:" in status else "-Beta"

	return revision

def GetCurrentBranchType():
    currentBranch = GetCurrentBranch() 
    if currentBranch is None:
        return '???'
    separatorindex = currentBranch.find('/')
    if separatorindex > 0:
        currentBranchType = currentBranch[0:separatorIndex].lower() 
    else:
        currentBranchType = currentBranch.lower()
    return currentBranchType

def GetCurrentBranch():
	platform = ("Windows" if os.name == "nt" else "Linux")

	git_check_commandline = ["git", "branch"] 
#   Sample output:
#        *  bugfix/QATE-30
#           feature/QATE-23
#           hotfix/QATE-18
#           master
# 	or in case of tag checkout
#        * (no branch)

    if platform == "Windows":
		git_check_commandline = ' '.join(git_check_commandline)
    try:
        tag_names = subprocess.Popen(git_check_commandline, stdout = subprocess.PIPE).communicate()[0].strip("\n")
        if len(tag_names) == 0:
			return None
		else:
			tags = tag_names.split("\n")
			if len(tags) == 0: 
				return None 
			else:
				branch = None
				for tag_ls in tags:
					if (tag_ls[0] == '*'): 
						branch = tag_ls[2:] 
						break

				if branch != "(no branch)":
					return branch
				else:
					# might be a tag checkout so we need to check
					git_check_commandline = ["git", "log", "-1", "--pretty=format:%H"]
					if platform == "Windows":
						git_check_commandline = ' '.join(git_check_commandline)
					revision = subprocess.Popen(git_check_commandline, stdout = subprocess.PIPE).communicate()[0].strip("\n")
					if len(revision) == 0:
						return None

					git_check_commandline = ["git", "name-rev", revision]
#					Sample output:
#						77ef3232f0ad1c5f78e8942cb69537f09a727720 tags/Trader_3.5.4^0
#					or
#						4de3f2367d3f095d0a6f1e8f411389195d55ba00 develop
					rev_name = subprocess.Popen(git_check_commandline, stdout = subprocess.PIPE).communicate()[0].strip("\n")
					if len(rev_name) == 0:
						return None
					if "tags/" in rev_name:
						return "tag"
	except Exception as ex:
		print str(ex)
		return None
	return None

def GetLatestGitTag(targetName):
	# TODO:
	# - iterate through all revisions (git log --pretty=format:%H) and find the latest applied tag (git show-ref --tags --dereference)
	platform = ("Windows" if os.name == "nt" else "Linux")

	#git_check_commandline = ["git", "ls-remote", "--tags"]
	#   Sample output:
	#	   8a2bb8f5114b7ea9a025b5e2f1447c01f8052a69         refs/tags/Controller_3.5.0
	#	   5bbb36e64815208da8ee42dab3df5459e93b69a2         refs/tags/Controller_3.5.0A{}
	#	   fO1a044470d4c0da576c36cb938554cf158a36c8         refs/tags/Trader_3.4.66a
	#	   e3cce809d10444a0lbd629fbe6bebalf254e0f98         refs/tags/Trader 3.5.1
	#	   5bbb36e64815208da8ee42dab3df5459e93b69a2         refs/tags/Trader 3.5.1A{}
	git_check_commandline = ["git", "tag", "-l", targetName + "_*", "--merged"]
	#   Sample output:
	# RamBooker 3.5.0 
	# RamBooker 3.5.1 
	# RamBooker 3.5.10 
	# RamBooker 3.5.11 
	# RamBooker 3.5.12
	# RamBooker 3.5.12a 
	# RamBooker 3.5.14 
	# RamBooker 3.5.15 
	# RamBooker 3.5.15a 
	# RamBooker 3.5.15b 
	# RamBooker 3.5.2
	# RamBooker 3.5.3 
	# RamBooker 3.5.4 
	# RamBooker 3.5.5 
	# RamBooker 3.5.6 
	# RamBooker 3.5.7 
	# RamBooker 3.5.8 
	# RamBooker 3.5.9



	if platform == "Windows":
		git_check_commandline = ' '.join(git_check_commandline)
	try:
		tag_names = subprocess.Popen(git_check_commandline, stdout = subprocess.PIPE).communicate()[0].strip("\n") 
		if len(tag_names) == 0:
			return None
		else:
			tags = tag_names.split("\n") 
			if len(tags) == 0:
				return None
			else:
				latest_tag = None 
				latest_major = None 
				latest_minor = None 
				latest_patch = None 
				latest_hotfix = None 
				for tag_ls in tags:
					tag = None
					match = re.match("(%s_[a-zA-Z0-9.]*)$" % targetName, tag_ls)
					if match and len(match.groups()) == 1:
						tag = match.groups()[0]
					else:
						continue

					tag_split = tag[len(targetName) + 1:].split(".")
					if len(tag_split) == 4:
						(major, minor, patch, hotfix) = tag_split
					elif len(tag_split) == 3:
						(major, minor, patch_and_hotfix) = tag_split

						patch = None
						hotfix = None
						match = re.match("([0-9]*)([a-zA-Z]*?)$", patch_and_hotfix)
						if match and len(match.groups()) == 2:
							patch = match.groups()[0]
							hotfix = match.groups()[1]
						else:
							raise Exception("Unable to parse patch_and_hotfix section of tag {0}".format(tag))
					else:
						continue #Obsolete tag format
					if latest_tag == None or (int(major) > int(latest_major) or int(minor) > int(latest_minor) or int(patch) > int(latest_patch) or ( str(hotfix) > str(latest_hotfix) and int(patch) >= int(latest_patch))):
						latest_tag = tag
						(latest_major, latest_minor, latest_patch, latest_hotfix) = (major, minor, patch, hotfix)
				return latest_tag
	except Exception as ex:
		print str(ex)
		return None




def GetLatestTaggedVersion(targetName, returnErrorInsteadOfException = False): 
	tag = GetLatestGitTag(targetName)
	if not tag:
		errorMsg = "Couldn't find any {0} tag.".format(targetName)
		if returnErrorInsteadOfException:
			return errorMsg
		raise Exception(errorMsg)

	tag_version_match = ExtractVersionFromString(tag[len(targetName) 1:])
	if not tag_version_match:
		errorMsg = "Latest tag {0} does not contain a valid version string.".format(tag)
		if returnErrorInsteadOfException:
			return errorMsg
		raise Exception(errorMsg)
	return tag_version_match.groups0[0]

def UpdateVersion(iVersionFilename, xmlFile, iMode):
	solution = ProjectParser.ParseSolutionAndProjects(xmlFile)
	if not solution:
		print "Unable to parse " + xmlFile
		sys.exit(-1)

	ateFolder = os.path.dirname(xmlFile)
	# handle case of projects with different configurations 
	if solution.Name == "TradeManager":
		solutionName = "TM"
	elif solution.Name.startswith("FHProxy"):
		solutionName = "FHProxy"
	elif solution.Name.startswith("Trader"):
		solutionName = "Trader"
	else:
		solutionName = solution.Name

	current_branch_type = GetCurrentBranchType()
	current_version = None
	if current_branch_type not in ['master', 'tag', 'release']:
		current_version = "0.0.0"
	else:
		current_version = GetLatestTaggedVersion(solutionName)
	new_revision = GetGitRevision(ateFolder)
	new_version = CheckAndFlagAsOfficial(solutionName, current_version + '.' + new_revision, ateFolder, iMode)
	if UpdateVersionFileIfNeeded(solutionName, new_version, iVersionFilename):
		print "Updated version file {0} with version {1}".format(iVersionFilename, new_version)
	else:
		print "Version file {0} already at version {1}".format(iVersionFilename, new_version)

if __name__ == "__main__":
	usage = "%prog [project xml file] [project version file] [mode nightly|official]"
	parser = optparse.OptionParser(usage) 
	(options, args) = parser.parse_args() 
	if len(args) < 2:
		parser.error("Missing required argument.")

	mode = args[2] if len(args) >= 3 else "nightly"

	retCode = 0
	try:
		UpdateVersion(args[1], args[0], mode) 
	except Exception as e:
		print "Error updating version: " + str(e) 
		retCode = 1
	sys.exit(retCode)
