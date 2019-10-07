from socket import gethostname

"""
Stores the configuration for the usual QATE dev servers, and provides
utility functions to figure out on what machine a script is running.
"""

class DevServer:
	def __init__(self, html_tests_root='', packages_root='', gcc='gcc', gpp='g++'):
		"""
		Stores information about a dev machine. All arguments are optional.

		Args:
			html_tests_root: Location to put HTML result of test runs 
			packages_root: Folder containing the compiled binaries 
			gcc: Name of the gcc binary to use (some machines use the
			   32-bit binary, while others compile in 64-bit)
			gpp: Name of the gpp binary
		"""
		self.html_tests_root = html_tests_root
		self.packages_root = packages_root
		self.gcc = gcc
		self.gpp = gpp

_machines = {
	# Main dev server
	'jp1sqated1' : DevServer(html_tests root=r'/qate_nas/build/http/root/QATE/tests'
							,packages_root=r'/qate_nas/build/package'),
	# New primary dev server
	'jplaqated001.jp.baml.com' : DevServer(html_tests_root=r'/qate_nas/build/http/root/QATE/tests',
							  packages_root=r'/qate_nas/build/package'),
	# London dev servers
	'lonqatluap001' : DevServer(html_tests_root=r'/qate_nas/QATE_UAT/config_server/root/QATE/tests'
							,packages_root=r'/qate_nas/QATE_UAT/config_server/root/QATE/package'), 
	'lonqatluap002' : DevServer(html_tests_root=r'/qate_nas/QATE_UAT/config_server/root/QATE/tests'
							,packages_root=r'/qate_nas/QATE_UAT/config_server/root/QATE/package'),

	# Weaker machine, used to run release tests
	# Package dir left empty because we may not normally want to do official 
	# builds on this machine
	'mk1sqadds1' : DevServer(h
	tml_tests_root=r'/qate_nas/build/http/root/QATE/tests' 
					,gcc=r1i386-redhat-linux-gcc'
					,gpp=r1i386-redhat-linux-g++'),

	# New dev server
	'jp1sqateq001.jpchbwb.baml.com' : DevServer(html_tests_root=r'/qate_nas/build/http/root/QATE/tests'
								  ,packages_root=r'/qate_nas/build/package'),

	# Dominic
	'ETY0WP56534' : DevServer(html_tests_root=r'C:\Working\test results\published'), 
	'F10604B7ED261' : DevServer(html_tests_root=r'C:\working\tests'),

	# Sergio
	'F10604B5C782E' : DevServer(html_tests_root=r'C:\Working\Dev\QATE trunk\tests\work\html')
}

def get devserver info():

  If the current host (server the script is running on) is in the machines 
  list, returns a DevServer instance for it. Otherwise, returns None.

  name = gethostname()
  if name in machines: 
     return machines[name] 
  else:
     return None

if name == ' main T:
  info = get devserver info() 
  print info
