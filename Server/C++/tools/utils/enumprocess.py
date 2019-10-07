"""
Enumerates active processes as seen under windows Task Manager on Win NT/2k/XP using PSAPI.dll 
(new api for processes) and using ctypes.Use it as you please.

Based on information from http://support.microsoft.com/default.aspx?scid=KB;EN-US;0175030&ID=KB;EN-US;Q175030

By Eric Koome
email ekoome@yahoo.com 
license GPL

2012/11/1 Modified by Dominic Morneau to return a list of (pid, processname, handle) instead of just printing the names 
Ref: http://code.activestate.com/recipes/305279/
"""

from ctypes import *

psapi = windll.psapi
kernel = windll.kernel32

def EnumProcesses():
	"""Returns a list(pid, name, handle)"""
	arr = c_ulong * 256
	lpidProcess= arr()
	cb = sizeof(lpidProcess)
	cbNeeded = c_ulong()
	hModule = c_ulong()
	count = c_ulong()
	modname = c_buffer(30)
	PROCESS_QUERY_INFORMATION = 0x0400 
	PROCESS_VM_READ = 0x0010

	#Call Enumprocesses to get hold of process id's 
	psapi.EnumProcesses(byref(lpidProcess),
						cb,
						byref(cbNeeded))

	#Number of processes returned
	nReturned = cbNeeded.value/sizeof(c_ulong())

	pidProcess = [i for i in lpidProcess][:nReturned]
	plist = []
	for pid in pidProcess:
		#Get handle to the process based on PID
		hProcess = kernel.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
									False, pid)
		if hProcess:
			psapi.EnumProcessModules(hProcess, byref(hModule), sizeof(hModule), byref(count)) 
			psapi.GetModuleBaseNameA(hProcess, hModule.value, modname, sizeof(modname))
			pname = str("".join([ i for i in modname if i != '\x00'))
			# Ignore empty process names (i.e. System)
			if pname:
				plist.append((int(pid), pname, hProcess))
			#-- Clean up
			for i in range(modname._length_):
				modname[i]='\x00'
			kernel.CloseHandle(hProcess)
	return plist

if __name__ == '__main__':
	EnumProcesses()
