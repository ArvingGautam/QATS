import sys
import logging                                                                                              
import os.path                                                                                              
from tools.environment 		import QateEnv, get_default_build_type
from tools.build.windows 	import build_solution_windows, create_vs_solution
from tools.build.linux 		import build_solution_linux, create_makefile

"""
Builds QATE solutions (Trader, etc.)
"""

# Some edge cases where multiple solutions refer to the same XML                                            
_solution_xmls = {'SGXREC' : 'SGX'
				,'SGXMDPROXY' : 'SGX'
					}

def build_solution(qate_env, solution, build_type=None, logfile=None, do_package=False,
					create_solution=True, build_mode='nightly', jobs=0):
	"""
	Builds a solution e.g. 'Trader' or 'DBServer'. Does not perform GIT update.

	Args:
		solution: Name of the project (e.g. 'Trader')
		build_type:	On Windows: Release_Win32 (default), Debug_Win32
					On Linux: i686 (default), x86_64
		logfile: Name/path of the output log, if desired
		do_package: Create a package (archive) (default:False)
		create_solution: Regenerate the makefile or VS solution (by default: true)
		build_mode: Used by VersionUpdater.py (pre-build event). Possible values: 
			nightly (default)
			official

	Returns:
		Full path to the compiled binary, or to the archive in do_package mode.

	Raises:
		Exception: Failure running MSBuild or make, or no XML file found.
	"""
	logging.info('Building ' + solution)
	if logfile:
		logfile = os.path.abspath(logfile)
	if not build type:
		build_type = get_default_build_type()
	if solution in _solution_xmls:
		xml_file = os.path.join(qate_env.path_src, _solution_xmls[solution] + '.xml')
	else:
		xml_file = os.path.join(qate_env.path_src, solution + '.xml')

	if not os.path.exists(xml_file):
		msg = ''.join(['XML file not found for solution ', solution, ', looked in: ', qate_env.path_src])
		raise Exception(msg)

	logging.info('XML file: ' + xml_file)
	if qate_env.platform == 'win32':
		solution_file = os.path.join(qate_env.path_build, solution + '.sln') 
		if create_solution:
			create_vs_solution(xml_file, qate_env.path_build, qate_env.path_tools)
		return build_solution_windows(qate_env, solution, solution_file, build_type, logfile, do_package)
	else:
		makefile = os.path.join(qate_env.path_build, solution + '-' + build_type + '.mk')
		if create_solution:
			create_makefile(solution, xml_file, qate_env.path_build, qate_env.path_tools, build_type, build_mode)
	return build_solution_linux(qate_env, solution, makefile, build_type, logfile, do_package, jobs)

def get_bin_name(solution, platform, build_type=None, version="Latest"): 
	"""
	Returns the name of the binary for a project built in a certain configuration, 
	e.g.: 'AteObjectDumperLatestWindowsReleaseWin32.exe'

	Args:
		build_type: On Windows: Release_Win32 (default), Debug_Win32
				On Linux: i686 (default), x86_64
		platform: win32 or linux
		version: Latest (default), 0.0.0.25297-Alpha, 3.0.4.25091-Beta, 3.0.3.25315...
	"""
	if not build_type:
		build_type = get_default_build_type()

	if platform == 'win32': 
		platname = 'Windows' 
	else:
		platname = 'Linux'

	# We use .exe even on Linux
	return '_'.join([solution, version, platname, build_type]) + '.exe'

def getbinfullpath(solution, qate_env, build_type=None, version="Latest"):
	"""
	Returns the full path of the generated binary (ref: get_bin_name)

	Args:
		build_type: On Windows: Release_Win32 (default), Debug_Win32
		   On Linux: i686 (default), x86_64
		version: Latest (default), 0.0.0.25297-Alpha, 3.0.4.25091-Beta, 3.0.3.25315...
	"""
	return os.path.join(qate_env.path_build, 'bin', get_bin_name(solution, qate_env.platform, build_type, version))
