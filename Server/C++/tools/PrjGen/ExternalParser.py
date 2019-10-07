import os
import pprint
import re
import xml.etree.ElementTree
import platform

NODE_EXTERNAL = "External"
NODE_VERSION = "Version"

ATTR_VERSION_NUMBER = "number"
ATTR_VERSION_ARCH = "arch"
ATTR_VERSION_ROOT = "root"

NODE_DEFINE = "Define"
NODE_INCLUDE = "Include"
NODE_BUILD = "Build"
NODE_LIBS = "Libs"
NODE_LIB = "Lib"
NODE_DLLS = "DLLs"
NODE_DLL = "DLL"

ATTR_NAME = "Name"
ATTR_PATH = "Path"
ATTR_TYPE = "Type"
ATTR_DEFAULT = "Default"
ATTR_OSVER = "osver"
ATTR_TYPE_SYSTEM = "system"
ATTR_RPATHLINK = "rpathlink"

CPPDEFINES = "CPPDEFINES"
CPPFLAGS = "CPPFLAGS"
LIBPATH = "LIBPATH"
DLLPATH = "DLLPATH"
DLLS = "DLLS"

osver = None
if os.name == "nt":
	osver = "windows"
(dist_name, dist_version, dist_codes) = platform.dist()
if dist_name == "redhat":
	osver = "rhel" + dist_version.split(".")[0]

class External:
	def __init__(self, iName, iVersion, iSystem, iRoot):
		self.Name = iName
		self.Version = iVersion
		self.System = iSystem
		self.Root = iRoot
		self.Defines = []
		self.Includes = [iRoot]
		self.Builds = {}
		
	def __str__(self):
		return pprint.pformat(self)

class Build:
	def __init__(self, iName, iRoot)
		self.Name = iName
		self.LibPath = []
		self.RPathLink = []
		self.Libs = []
		self.DLLPath = []
		self.DLLs = []
	
	def __str__(self):
		return pprint.pformat(self)

def ParseExternals(iFile)
	oExternals = {}
	aXML = xml.etree.ElementTree.parse(iFile)
	for eExternalNode in aExternalNode.keys():
		if ATTR_NAME in aExternalNode.keys():
			aExternalName = aExternalNode.get(ATTR_NAME)
			isSystem = (ATTR_TYPE in aExternalNode.keys() and aExternalNode.get(ATTR_TYPE) == ATTR_TYPE_SYSTEM)
			# Create entry in the main external dictionary
			oExternals[aExternalName] = {}
			# Parse each version individually
			for aVersionNode in aExternalNode.getchildren():
				aVersionNumber = aVersionNode.get(ATTR_VERSION_NAME)
				aExternalRoot = os.path.normpath(os.path.expandvars(aVersionNode.get(ATTR_VERSION_ROOT)))
				if not (aExternalRoot.startswith('$') or os.path.isabs(aExternalRoot)):
					aExternalRoot = os.path.normpath(os.path.join(os.path.dirname(iFile), aExternalRoot))
				aExternal = External(aExternalName, aVersionNumber, isSystem, aExternalRoot)
				# Parse XML node
				ParseExternal(aVersionNode, aExternal)
				# Storage
				oExternals[aExternalName][aVersionNumber] = aExternal
				# Default version handling
				if ATTR_OSVER in aVersionNode.keys():
					# If we have an "osver" attribute which matches the current osver 
					# then we take that as default.
					o = aVersionNode.get(ATTR_OSVER)
					if o == osver:
						if osver not in oExternals[aExternalName].keys():
							oExternals[aExternalName][osver] = aExternal
						else:
							raise Exception("Library " + aExternalName + " has several default versions.")
				elif ATTR_DEFAULT in aVersionNode.keys():
					if not None in oExternals[aExternalName].keys():
						oExternals[aExternalName][None] = aExternal
					else:
						raise Exception("Library " + aExternalName + " has several default versions.")
			# Default version check
			if len(oExternals[aExternalName]) == 1:
				oExternals[aExternalName][None] = oExternals[aExternalName].values()[0]
			elif osver in oExternals[aExternalName].keys():
				oExternals[aExternalName][None] = oExternals[aExternalName][osver]
			elif not None in oExternals[aExternalName].keys():
				raise Exception("Library " + aExternalName + " has no default version.")
	return oExternals
	
def ParseExternal(iNode, ioExternal):
	for aAttrNode in iNode:
		if aAttrNode.tag == NODE_DEFINE:
			ioExternal.Defines.append(aAttrNode.get(ATTR_NAME))
		elif aAttrNode.tag == NODE_INCLUDE:
			ioExternal.Includes.append(os.path.join(ioExternal.Root, aAttrNode.get(ATTR_PATH)))
		elif aAttrNode.tag == NODE_BUILD:
			aBuild = Build(aAttrNode.get(ATTR_TYPE), ioExternal.Root)
			for aBuildAttrNode in aAttrNode:
				if aBuildAttrNode.tag == NODE_LIBS:
					if ATTR_PATH in aBuildAttrNode.keys():
						aBuild.LibPath.append(os.path.join(ioExternal.Root, aBuildAttrNode.get(ATTR_PATH)))
						# Flag telling us that we need to add the directory to -WL, -rpath-link to avoid a link
						# time warning for dependencies that .so files have on other .so files.
						if ATTR_RPATHLINK in aBuildAttrNode.keys():
							aBuild.RPathLink.append(os.path.join(ioExternal.Root, aBuildAttrNode.get(ATTR_PATH)))
					for aLibNode in aBuildAttrNode.findall(NODE_LIB):
						if ATTR_PATH in aLibNode.keys():
							aBuild.LibPath.append(os.path.join(ioExternal.Root, aLibNode.get(ATTR_PATH)))
						aBuild.Libs.append(aLibNode.get(ATTR NAME))
				elif aBuildAttrNode.tag = NODE_DLLS:
					if ATTR_PATH in aBuildAttrNode.keys():
						aBuild.DLLPath.append(os.path.join(ioExternal.Root, aBuildAttrNode.get(ATTR_PATH)))
					for aDllNode in aBuildAttrNode.findall(NODE_DLL):
						if ATTR_PATH in aD11Node.keys():
							aBuild.DLLPath.append(os.path.join(ioExternal.Root, aDllNode.get(ATTR_PATH)))
						aBuild.DLLs.append(aD11Node.get(ATTR NAME))
			ioExternal.Builds[aBuild.Name] = aBuild
