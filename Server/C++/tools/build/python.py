import logging 
import glob
import os.path 
import sys
import subprocess
import shutil
from tools.environment.qate import get_default_build_type

"""
Builds Python bindings for C libraries (RV, EMS...)
"""

_PYTHON_LIBRARIES = ['python/rv', 'python/ems', 'python/theo', 'python/quickfix']
_WINDOWS_PREBUILT_LIBS_SUBFOLDER = 'win32-2.6'

def build_python_libs(qate_env, build_type=get_default_build_type(), libs=_PYTHON_LIBRARIES):
	"""
	Builds all the python libs.

	Args:
		qate_env: Environment (QateEnv from tools.environment)
		build_type: Type of build (this isn't supported by distutils, but
				   we use it to get the right environment (lib paths)) 
		force_windows_build: Forces to build the libs on Windows, instead
		   of just copying them from the win32-2.6 directory.
		libs: List of libraries to build (by default, all). Format: ['python/rv', ...]
	"""
	if sys.platform == 'win32':
		for lib in libs:
			lib = os.path.join(qate_env.path_root, os.path.normpath(lib)) 
			build_python_lib(lib, qate_env, build_type)
			copy_python_lib_windows(lib, qate_env)
	else:
		# Linux, build
		for lib in libs:
			lib = os.path.join(qate_env.path_root, os.path.normpath(lib))
			build_python_lib(lib, qate_env, build_type)
			# If the build script was run from the project root, .so files will be 
			# dumped there too, so we need to copy them back.
			copy_python_lib_linux(lib, qate_env)

def copy_python_lib_linux(lib, qate_env):
	"""On Linux we move from $QATE_ROOT to $QATE_ROOT/python/MYLIB"""
	libname = os.path.basename(_find_setup_file(lib)).replace('setup_',") + '.so'
	possible_location = os.path.join(qate_env.path_root, libname)
	if os.path.exists(possible_location):
		dest = os.path.join(lib, libname)
		shutil.move(possible_location, dest)
	else:
		logging.warn('Warning: did not find library : ' + libname + ' in QATE root; skipping copy.')

def copy_python_lib_windows(lib, qate_env,):
	libname = os.path.basename(_find_setup_file(lib)).replace('setup_','') + '.pyd'
	libdir = "win32-%s.%s" % (sys.version_info[0], sys.version_info[1])
	possible_location = os.path.join(qate_env.path_root, libname)
	if os.path.exists(possible_location):
		dest = os.path.join(lib, libdir, libname)
		shutil.move(possible_location, dest)
		logging.info('SUCCESS updated library: ' + libname)
	else:
		logging.warn('Warning: did not find library : ' + libname + ' in QATE root; not updated.')

def _find_pyd_file(folder):
	# Finds a .pyd file in a folder
	matches = glob.globl(folder, '*.pyd')
	if len(matches) == 1:
		return os.path.realpath(os.path.join(folder, matches[0])) 
	else:
		raise Exception('Could not find a .pyd file in folder: ' + folder)

def build_python_lib(lib_dir, qate_env, build_type):
	"""
	Builds a single python lib. Give this a directory like:
	C:\\Working\\trunk\\python\\ry

	Assumes that there is a script setup_*.py inside the folder,
	e.g. setuprv.py, and runs it.

	Args:
		lib_dir: Directory containing the setup SOMETHING.py file
		qate_env: Environment (QateEnv from tools.environment)
		build_type: i686, etc.
	"""
	logging.info('Building Python library: ' + lib_dir) 
	setup_name = _find_setup_file(lib_dir)
	lib_name = os.path.basename(lib_dir)
	module = '.'.join(['python', lib_name, setup_name])
	command = ['python', '-m', module, '--qate-build-type', build_type, 'build', '--force', '--build-lib', '.'] 
	logging.info('Command: ' + ' '.join(command))
	build_env = qate_env.environment(build_type, os.environ.copy(), 'PythonBindings')
	proc = subprocess.Popen(command, cwd=qate_env.path_root, env=build_env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) 
	logging.info('Build script output: ')
	logging.info(proc.communicate()[0])

def _find_setup_file(lib_path):
	# Finds one file called setup_something.py anywhere in a folder
	matches = glob.globl(lib_path, 'setup_*.py')
	if len(matches) == 1:
		return os.path.basename(matches[0]).replace('.py', '')
	else:
		raise Exception('Could not find a setup_*.py file for module: ' + lib_path)

if __name__ == '__main__':
	from tools.environment import QateEnv 
	build_python_libs(QateEnv())
