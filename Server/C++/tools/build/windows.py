import logging 
import subprocess
import os.path 
import time
from tools.PrjGen.ProjectParser import ParseSolutionAndProjects
from tools.PrjGen.VS2015Generator import GenerateVS2015Files

"""
Builds a solution in a Windows environment and generates VS projects via PrjGen.
"""

_MSBUILD_KEY 		= r'SOFTWARE\Microsoft\MSBuild\ToolsVersions\14.0'
_MSBUILD_KEY_NAME 	= 'MSBuildToolsPath'
_MSBUILD_EXE_NAME 	= 'MSBuild.exe'

def _get_msbuild_path():
	"""Gets path to msbuild.exe via Windows registry"""
	# _winreg exists only on Windows, so we import it here.
	import _winreg
	reg = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)
	key = _winreg.OpenKey(reg, _MSBUILD_KEY)
	# Randomly put 10, but the idea is just to loop over the keys until we find the right one
	for i in range(10):
		(name, data, type) = _winreg.EnumValue(key, i)
		if name == _MSBUILD_KEY_NAME:
			break
	assert(name == _MSBUILD_KEY_NAME)
	_winreg.CloseKey(key) 
	_winreg.CloseKey(reg)
	return os.path.join(data, _MSBUILD_EXE_NAME)

def _quote(str):
	return '"' + str + '"'

def build_solution_windows(qate_env, solution, solution_file, build_type, logfile=None, do_package=False):
	"""
	Platform-specific; builds a .sln file on Windows.

	Args:
		qate_env: Environment, used for the working dir
		solution: Solution name (not used currently)
		solution file: Path to .sln
		build_type: e.g. Release Win32
		logfile: Logfile for MSBuild to write into (default: stdout)
		do package: Package the resulting binaries into a ZIP file (release builds only)
	"""
	if do_package:
		if 'Release' in build_type:
			build_type = build_type.replace('Release', 'Package')
		else:
			logging.warn('Attempting to package a non-release build; build type is: ' + build_type)

	(config, platform) = build_type.split('_')

	msbuild = _get_msbuild_path()
	command = []
	command.append(_quote(msbuild))
	command.append(_quote(solution_file))
	command.append('/t:Build')
	command.append('/p:Configuration=' + config)
	command.append('/p:Platform=' + platform)
	command.append('/m') # parallel build
	command.append('/nr:false')
	
	command.append('/v:n')
	if logfile:
		command.append('/1:FileLogger,Microsoft.Build.Engine;append=true;encoding=utf-8;logfile="' + logfile + '"')
	command_text = ' '.join(command)
	logging.info('Calling MSBuild: ' + command_text)
	start = time.time()
	subprocess.check_call(command_text)
	end = time.time()
	logging.info('Completed in ' + str(end - start) + ' seconds.')

def create_vs_solution(xml_file, build_root, tools_root):
	"""
	Calls the solution generator, creating .slnlevcxproj files, etc.
	in the build directory.

	Args:
		xml_file: Full path to e.g. DBServer.xml
		build_root: Output directory
		tools_root: Path to Python tools (e.g. C:\working\trunk\tools)
	"""
	logging.info('Generating VS2015 solution')
	solution = ParseSolutionAndProjects(xml_file, verbose=False)
	GenerateVS2015Files(solution, build_root, tools_root)
                                                                
																
																