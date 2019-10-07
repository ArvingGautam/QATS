import optparse
import os 
import re

RE_VERSION_STRING = re.compile(r"([^\"\.]+\.[^\.]+\.[^\.\"]+)(?:\.([^\"]*))?")

def ExtractVersion(iVersionFilename):
	if os.path.exists(iVersionFilename):
		return RE_VERSION_STRING.search(open(iVersionFilename, 'r').read())
	return None

def ExtractVersionFromString(iVersionString):
	return RE_VERSION_STRING.search(iVersionString)

if __name__ == "__main__":
	usage = "%prog [Version file]"
	parser = optparse.OptionParser(usage)
	(options, args) = parser.parse_args()
	if len(args) < 1:
		parser.error("Missing required argument.")
	version_match = ExtractVersion(args[0])
	if version_match != None:
		print version_match.group(0)
	else:
		print "0.0.0.0"
