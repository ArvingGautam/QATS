import sys

"""
Small utilities related to build types, e.g. Release Win32 or i686.
"""

def is_supported_build_type(type):
	return type in ['Release_Win32', 'Debug_Win32', 'i686', 'x86_64']

def get_default_build_type():
	"""On Windows, returns a Release_Win32 build; on Linux, i686"""
	if sys.platform == 'win32':
		return 'Release_Win32'
	else:
		return 'i686'

def get_platform():
	"""Returns Windows or Linux""" 
	if sys.platform == 'win32': 
		return 'Windows'
	else:
		return 'Linux'
