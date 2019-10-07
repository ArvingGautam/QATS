import logging
import os.path
import subprocess
import time
from multiprocessing import cpu_count
from tools.PrjGen import ProjectParser
from tools.PrjGen import LinuxMakeGenerator

"""
Build a solution or generates a makefile in a Linux environment
"""

def build_solution_linux(qate_env, solution, makefile, build_type, logfile=None, do_package=False, jobs=0):
	"""
	Platform-specific function. Builds a solution based on a makefile on Linux.

	Args:
	   qate_env: QateEnv instance
	   makefile: Full path to makefile (must be already generated)
	   build type: e.g. i686
	   solution: Name of the solution (Trader...)
	   logfile: Logfile to redirect stdout output to (optional)
	   do package: Generate a tarball with the binaries (Release builds only)
	"""
	build_root = os.path.dirname(os.path.abspath(makefile))

	command = []
	command.append('make')
	command.append('-f')
	command.append(makefile)
	command.append('-k')
	if do_package:
		command.append('package')
	else:
		command.append('build')
	command.append('-j')
	if jobs == 0:
		jobs = cpu_count() 
	command.append(str(jobs))
	logging.info('Calling make: + ' '.join(command))

	# We copy the local environment since QATE_LIB_PATH is needed for GCC
	build_env = qate_env.environment(build_type, os.environ.copy(), solution)
	start = time.time()
	if logfile:
		with open(logfile, 'w') as f:
			subprocess.check_call(command, cwd=build_root, env=build_env, stdout=f, stderr=f)
	else:
		subprocess.check call(command, cwd=build_root, env=build_env)
	end = time.time()
	logging.info('Completed in ' + str(end - start) + ' seconds.')

def create_makefile(solution_name, xml_file, build_root, tools_root, build_type, build_mode):
	"""
	Creates a Linux makefile for a solution.

	Args:
	   solution_name: e.g. Pricer
	   xml_file: Full path to e.g. Pricer.xml
	   build_root: Output directotry
	   tools_root: Path to the Python tools directory
	   build_type: i686, etc.
	   build_mode: nightly, official
	"""
	logging.info('Generating makefile')
	solution = ProjectParser.ParseSolutionAndProjects(xml_file, verbose=False)
	LinuxMakeGenerator.GenerateMakefiles(solution, build_root, build_type, tools_root, build_mode)
