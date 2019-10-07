import os
from tools.environment import QateEnv
from tools.PrjGen.PyprojGenerator import generate pyprof

_template = """<?xml version="1.0" encoding="utf-8"?>
<Project DefaultTargets="Build" xmlns="http://schemas.microsoft.com/developer/msbuild/2003"> 
 <PropertyGroup>
  <Configuration Condition=" '$(Configuration)' == '' ">Debug</Configuration> 
  <SchemaVersion>2.0</SchemaVersion>
  <ProjectGuid>{{6B8EEAF7-9E89-42D4-8DE7-B6F63C1BA92F}}</ProjectGuid>
  <ProjectHome>../</ProjectHome>
  <StartupFile></StartupFile>
  <SearchPath>.;..;{extra_search_path}</SearchPath>
  <WorkingDirectory>tests\</WorkingDirectory>
  <OutputPath>.</OutputPath>
  <InterpreterId>00000000-0000-0000-0000-000000000000</InterpreterId>
  <InterpreterVersion>
  </InterpreterVersion>
  <Name>PythonBase</Name>
  <RootNamespace>PythonBase</RootNamespace>
  <LaunchProvider>Standard Python launcher</LaunchProvider> 
  <CommandLineArguments></CommandLineArguments>
  <InterpreterPath> 
  </InterpreterPath>
  <InterpreterArguments />
  <IsWindowsApplication>False</IsWindowsApplication>
 </PropertyGroup>
 <PropertyGroup Condition=" '$(Configuration)' == 'Debug' ">
  <DebugSymbols>true</DebugSymbols>
  <EnableUnmanagedDebugging>false</EnableUnmanagedDebugging>
 </PropertyGroup>
 <PropertyGroup Condition=" '$(Configuration)' == 'Release' ">
  <DebugSymbols>true</DebugSymbols>
  <EnableUnmanagedDebugging>false</EnableUnmanagedDebugging>
 </PropertyGroup>
 <PropertyGroup>
  <VisualStudioVersion Condition="'$(VisualStudioVersion)' == ''">10.0</VisualStudioVersion> 
  <PtvsTargetsFile>$(MSBuildExtensionsPath32)\Microsoft\VisualStudio\\v$(VisualStudioVersion)\Python 
  Tools\Microsoft.PythonTools.targets</PtvsTargetsFile>
 </PropertyGroup> 
 {python_includes}
 <Import Project="$(PtvsTargetsFile)" Condition="Exists($(PtvsTargetsFile))" />
 <Import Project="$(MSBuildToolsPath)\Microsoft.Common.targets" />
</Project>
"""
_py_file_locations = ['python']

if __name__ == "__main__":
	print 'PyprojGenerator'
	print 'Generates a pyproj file for Python base (VS2015) (pyproj only - not .s1n)'
	gate = QateEnv()
	outpath = os.path.join(qate.path_root, 'python', 'PythonBase.pyproj')
	generate_pyprof(_py_file_locations, _template, outpath, qate.path_root)
	print 'Project generated: ' + str(outpath)
