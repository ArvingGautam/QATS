import os.path 
import sys
import logging 
import subprocess 
import shutil
from tools import ATEObjectPyGenerator
from tools.build.build import build_solution, get_bin_fullpath

def dump_ate_objects(qate_env, output_dir=None, do_rebuild=True, solution='AteObjectDumper', build_type=None): 
	""""
	Builds the AteObjectDumper, then dumps the objects to a file.

	Args:
		qate_env: QateEnv instance
		output_dir: Directory to save Python dumper output (default: build_root)
			AteObjectDumper-Objects.xml is always saved in QATE root for now. 
		do_rebuild: Rebuild the AteObjectDumper solution first (default: True)
		solution: Name of the solution to dump objects for (default: 'AteObjectDumper').
			TODO: Check if it matters. Probably not.
		build type: Type of build to use (Release_Win32...)
	"""
	if not output_dir:
		output_dir = qate_env.path_build
	if do_rebuild:
		logging.info('Preparing to dump ATE objects, build type: ' + build_type)
		build_solution(qate_env, 'AteObjectDumper', build_type=build_type)
	_run_ate_dumper(qate_env, qate_env.path_root, build_type)
	_run_python_generator(qate_env, output_dir)

def _run_ate_dumper(qate_env, output_dir, build_type):
	# Calls the AteObjectDumper executable
	dumper_path = get_bin_fullpath('AteObjectDumper', qate_env, build_type)
	command = []
	command.append(dumper_path)
	command_text = ' '.join(command)
	logging.info('Calling ATE dumper: ' + command_text)
	libs_env = qate_env.environment(build_type, {}, 'AteObjectDumper')
	logging.info('PATH is: ' + libs_env.get('PATH', ''))
	logging.info('LD LIBRARY PATH is: ' + libs_env.get('LD_LIBRARY_PATH', '')) 
	return subprocess.check_call(command, env=libs_env, cwd=output_dir)

def _run_python_generator(qate_env, output_dir):
	# Transform the XML dump into a .py file
	logging.info('Generating AteObjects.py from AteObjectDumper-Objects.xml')
	dump_file = os.path.join(qate_env.path_root, 'AteObjectDumper-Objects.xml')
	if not os.path.exists(dump_file):
		raise Exception("Error: AteObjectDumper-Objects.xml not found. "
					"Expected path: " + dump_file)
	ATEObjectPyGenerator.readFromXML(qate_env.path_root, dump_file) 
	ATEObjectPyGenerator.generateAteObjects(qate_env.path_root) 
	ATEObjectPyGenerator.generateDBMapping(qateenv.path_root)
