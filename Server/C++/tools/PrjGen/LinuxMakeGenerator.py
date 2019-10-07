import cStringlO
import optparse
import os
import platform
import pprint
import ExternalParser 
import ProjectParser

INCLUDE_FOLDER = "include" 
SOURCE_FOLDER = "src"

class StringBuilder:
	def __init__ (self):
		self.out = cStringIO.StringIO()
		return
	def write(self, str):
		self.out.write(str)
		return
	def writeL(self, str):
		self.out.write(str)
		self.out.write("\n")
		return
	def endl(self):
		self.out.write("\n")
	def writeHdr(self, str):
		self.out.write("\n##############################\n")
		self.out.write("#\n")
		self.out.write("# ")
		self.out.write(str);
		if str[len(str)-1] != "\n":
			self.out.write("\n")
		self.out.write("#\n")
		self.out.write("##############################\n\n")
		return
	def getString(self):
		return self.out.getvalue()


def GenerateMakefiles(solution, output_folder, build=None, tools_folder=None, mode="nightly"):
	if build != None:
		if not build in solution.AvailableBuilds:
			raise Exception("Build type " + build + " is not available on this platform.\nAvailable build types: " + pprint.pformat(solution.AvailableBuilds)) 
		for target in solution.Targets.values():
			GenerateMakefile(solution, target, output_folder, build, tools_folder, mode)
	else:
		for build in solution.AvailableBuilds:
			GenerateMakefiles(solution, output_folder, build, tools_folder, mode)


def IsProjectExecutable(project):
	return (project.Type == "exe")


def IsProjectStaticLibrary(project):
	return ((not IsProjectExecutable(project)) and (len(project.Projectlncludes) == len(project.ProjectDependencies) == 0))


def GenerateProjectRecipes(solution, project, build, tools_folder, Makefile body, Makefile_recipes):
	project_name = project.Name.upper()
	# Includes and #defines
	includes = project_name + "_INCLUDES := -I" + os.path.join(project.Root, INCLUDE_FOLDER) + ' '
	for project_dependency in project.ProjectIncludes.values() + project.ProjectDependencies.values(): 
		includes += "-I" + os.path.join(project dependency.Root, INCLUDE_FOLDER) + ' '
		defines = project_name + "_DEFINES := "
	for define in project.Defines:
		defines += "-D" + define + ' '
	for external in project.ExternalDependencies:
		for include in external.Includes:
			includes += "-I" + include + ' '
		for define in external.Defines:
			defines += "-D" + define + ' '
	# Sources
	source_dir = project_name + "_SOURCE_DIR := " + os.path.join(project.Root, SOURCE_FOLDER)
	source dirs = project_name + "_SOURCE_DIRS := "
	for source_folder in project.Sources:
		source_folder = source_folder.replace(os.path.join(project.Root, SOURCE_FOLDER), "({project}_SOURCE_DIR)".format(project = project_name))
		source_dirs += source_folder + ' '
	sources = "(project)_SOURCES := $(foreach source_folder,$({project}_SOURCE_DIRS),$(wildcard $(source_folder)/*.cpp))".format(project = project_name)
	# Objects
	object_dir = project_name + "_OBJECTS_DIR := $(OUTPUT_DIR)/objects/" + project.FullName + "/$(BUILD)"
	object_dirs = "{project}_OBJECTS_DIRS := $(subst $({project}_SOURCE_DIR),$((project}_OBJECTS_DIR),$({project}_SOURCE_DIRS))".format(project = project_name)
	objects = "{project}_OBJECTS := $(subst $({project}_SOURCE_DIR),$({project}_OBJECTS_DIR),$({project}_SOURCES:.cpp=.0))".format(project = project_name)
	deps = "{project}_DEPS := $(patsubst %.o,%.d,$({project}_OBJECTS))".format(project = project_name) 
	# Write common definitions to Makefile
	Makefile_body.writeHdr(project.FuliName + " targets:")
	Makefile_body.writeL(includes)
	Makefile_body.writeL(defines)
	Makefile_body.writeL(source_dir)
	Makefile_body.writeL(source_dirs)
	Makefile_body.writeL(sources)
	Makefile_body.writeL(object_dir)
	Makefile_body.writeL(object_dlrS)
	Makefile_body.writeL(objects) 
	Makefile_body.writeL(deps)
	# Target
	target = project_name + "_TARGET := " 
	if IsProjectExecutable(project):
		# Executable
		target += project.GetTargetExecutable("$(OUTPUT_DIR)", "Linux", "$(BUILD)", version = "Latest")
		versioned_target = project_name + "_VERSIONED_TARGET := " + project.GetTargetExecutable("$(OUTPUT_DIR)", "Linux", "$(BUILD)", version = "$(GIT VERSION)")
		lib_path = project_name + "_LIBPATH := "
		libs = project_name + "_LIBS := $(SYSLIBS) "
		external_objects = project_name + "_EXTERNAL_OBJECTS = "
		external_libraries = project_name + "_EXTERNAL_LIBRARIES = "
		for project_dependency in project.ProjectIncludes.values() + project.ProjectDependencies.values():
			if IsProjectStaticLibrary(project_dependency):
				lib_path += "-L" + os.path.join("$(OUTPUT_DIR)", "lib", "$(BUILD)") + ' '
				libs += "-1" + project dependency.FullName + ' '
				external_libraries += "$(" + project_dependency.Name.upper() + "_TARGET) "
			else:
				external_objects += "$(" + project_dependency.Name.upper() + "_TARGET) "
		for external in project.ExternalDependencies:
			for path in external.Builds[build].LibPath:
				lib_path += "-L" + path + ' '
			for lib in external.Builds[build].Libs:
				libs += "-1" + lib + ' '
			for rpath in external.Builds[build].RPathLink:
				# Add -rpath-link to the linker to make ld look for shared library dependencies in non-standard places.
				lib_path += "-W1,-rpath-link " + rpath + ' '
		target_recipe = "({project}_TARGET): $({project}_OBJECTS) $({project}_EXTERNAL_LIBRARIES) $((project}_EXTERNAL_OBJECTS) | $(BIN_DIR)\n".format(project = project_name) 
		target_recipe += "\t$(CC) $({project}_OBJECTS) $({project}_EXTERNAL_OBJECTS) $(LINKFLAGS) $({project)_LIBPATH) $({project}_LIBS) -o $@".format(project = project_name) 
		versioned_target_recipe = "({project} VERSIONED_TARGET): $({project}_TARGET) | $(BIN_DIR)\n".format(project = project_name)
		versioned_target_recipe += "\tcp $< $@"
		package = project_name + "_PACKAGE := $(PACKAGE_DIR)/" + project.FullName + "_$(GIT VERSION)_Linux_$(BUILD).tar.gz"
		package_recipe = "$({project}_PACKAGE): $({project}_VERSIONED_TARGET) | $(PACKAGE_DIR)\n".format(project = project_name)
		package_recipe += "\tpython {tools_folder}/Packaging/PackageBinary.py {solution_file} {build_type} {project_name} -b $(OUTPUT_DIR) -o $(PACKAGE_DIR)".format(tools_folder, solution_file = solution.file, build_type = build, project_name = project.name)
		# Write to Makefile
		Makefile_body.writeL(lib_path)
		Makefile_body.writeL(libs)
		Makefile_body.writeL(external_objects)
		Makefile_body.writeL(external_libraries)
		Makefile_body.writeL(target)
		Makefile_body.writeL(versioned_target)
		Makefile_body.writeL(package)
		Makefile_recipes.writeL(target_recipe)
		Makefile_recipes.writeL(versioned_target_recipe)
		Makefile_recipes.writeL(package_recipe)
	elif IsProjectStaticLfbrary(project):
		# Static library
		target += os.path.join("$(OUTPUT_DIR)", "lib", "$(BUILD)", "lib" + project.FullName + ".a")
		target_recipe = "$({project}_TARGET): $({project}_OBJECTS) | $(LIB_DIR)\n".format(project = project_name)
		target_recipe += "\t$(LD) $(LDOPTIONS) $@ $({project}_OBJECTS)".format(project = project_name)
		# Write to Makefile
		Makefile_body.writeL(target)
		Makefile_recipes.writeL(target_recipe)
	else:
		target += "$({project}_OBJECTS)".format(project = project_name)
		# Write to Makefile
		Makefile_body.writeL(target)
	# Object recipe
	object_recipe = "$({project}_OBJECTS): $((project}_OBJECTS_DIR)%.o: $({project}_SOURCE_DIR)/%.cpp | $((project}_OBJECTS_DIRS)\n".format(project = project_name)
	object_recipe += "\t$(CC) $(CFLAGS_ALL) $({project}_INCLUDES) $((project)_DEFINES) $< -o $@".format(project = project_name)
	# Deps recipe
	deps_recipe = "$({project}_DEPS): $({project}_OBJECTS_DIR)/%.d: $({project}_SOURCE_DIR)/%.cpp | $({project}_OBJECTS_DIRS)\n".format(project = project_name)
	deps_recipe += "\t$(CC) $(CFLAGS_ALL) $((project}_INCLUDES) $({project}_DEFINES) -MM -MP $< -o $@".format(project = project_name)
	# Write to Makefile
	Makefile_recipes.writeL(object_recipe)
	Makefile_recipes.writeL(deps_recipe)


def GenerateMakefile(solution, target, output_folder, build, tools_folder=None, mode="nightly"): 
	output_folder = os.path.abspath(output_folder)
	if not tools_folder:
		tools_folder = os.path.normpath(os.path.join(os.path.dirname(solution.File), "..", "tools"))
	if not os.path.exists(output_folder):
		os.makedirs(output_folder)

	# 2. Generate Makefile in memory
	Makefile_body = StringBuilder()
	Makefile_recipes = StringBuilder()
	Makefile_body.writeHdr("{target_fullname}_(build_type).mk: automatically generated by Python\n".format(target_fullname = target.FullName, build_type = build))

	Makefile_body.writeHdr("Include Makefiles (COMMON):")
	gcc_prefix = ""
	(dist_name, dist version, dist_code) = platform.dist()
	native build = False
	if native_build and dist_name = "redhat" and int(dist version.split('.')[0]) >= 6:
		gcc_version = "4.7.2"
	else:
		gcc_version = "4.8.4"
	Makefile_body.writeL("""ifndef QATE_LIB_ROOT
$(error QATE_LIB_ROOT environment variable is not defined) 
endif
LD = ar
QATE_CC_BOOTSTRAP_PATH = $(QATE_LIB_ROOT)/fsf/gcc/(0)/.exec/x86-64.rhel.5
CC = $(QATE_CC_BOOTSTRAP_PATH)/bin/{1)g++
""".format(gcc version, gcc_prefix))
	Makefile_body.writeL("BUILD := " + build)
	Makefile_body.writeL("HOST := $(shell hostname)")
	Makefile_body.writeL("DEV_ROOT := " + os.path.normpath(os.path.join(os.path.dirname(solution.File), "..")))
	Makefile_body.writeL("include {output_folder}/cc_flags{build_type).mk".format(output_folder = output_folder, build_type = build))
	Makefile_body.writeHdr("Extract GIT version:")
	if target.VersionFile:
		prjgen_folder = os.path.join(tools_folder, "PrjGen")
		Makefile_body.writeL("GIT VERSION := $(shell python {prjgen_folder}/Version.py {project_xml} {build mode} > /dev/null && python {prjgen_folder}/VersionParser.py {versio_file})".format(prjgen_folder = prjgen_folder, 
			project_xml = solution.File,
			version_file = target.VersionFile,
			build_mode=mode))
	else:
		Makefile_body.writeL("GIT VERSION := 0.0.0.0")
	Makefile_body.writeHdr("Output folders:")
	Makefile_body.writeL("OUTPUT_DIR := " + output_folder)
	Makefile_body.writeL("LIB_DIR := $(OUTPUT_DIR)/lib/$(BUILD)")
	Makefile_body.writeL("BIN_DIR := $(OUTPUT_DIR)/bin")
	Makefile_body.writeL("PACEAGE_DIR := $(00TPUT_DIR)/package")

	for project in solution.Projects.values():
		GenerateProjectRecipes(solution, project, build, tools_folder, Makefile_body, Makefile_recipes)

	Makefile_body.writeHdr("Main targets:")
	Makefile_body.writeL(".PHONY: all package build clean")
	Makefile_body.writeL("all: package")
	Makefile_body.writeL("package: " + "$({target}_PACKAGE)".format(target = target.Name.upper())) 
	Makefile_body.writeL("build: " + "$({target}_IARGET)".format(target = target.Name.upper()))

	Makefile_body.writeHdr("Common recipes:")
	Makefile_body.writeL(Makefile_recipes.getString())
	dirs_recipe = "$(LIB_DIR) $(BIN_DIR) $(PACKAGE_DIR) "
	for project in solution.Projects:
		dirs_recipe += "({project}_OBJECTS_DIRS) ".format(project = project.upper())
		dirs_recipe += ":\n"
		dirs_recipe += "\tmkdir -p $@" 
	Makefile_body.writeL(dirs_recipe) 
	clean_recipe = "clean:\n"
	for project in solution.Projects: 
		clean_recipe += "\trm -f "
		clean_recipe += "({project}_TARGET) $({project}_OBJECTS) $({project}_DEPS) ".format(project = project.upper())
		clean_recipe += "\n"
	Makefile_body.writeL(clean recipe)

	Makefile_body.writeHdr("Dependencies:")
	for project in solution.Projects:
		Makefile body.writeL("-include $({project} DEPS)".format(pro]ect = project.upper()))

	# 3. Write Makefile to disk: 
	Makefile name = os.path.join(output folder, target.FullName + ' ' + build + ".mk")
	Makefile = open(Makefile name, 'wb')
	Makefile.write(Makefile body.getString())
	Makefile.close()

	# 4. Link cc flags.mk file if needed
	cc_flags_file = "cc_flags_" + build + ".mk"
	if not os.path.exists(os.path.join(output_folder, cc_flags_file)):
		os.symlink(os.path.join(os.path.dirname(solution.File), "make", cc_flags_file), os.path.join(output_folder, cc_flags_file))

	return Makefile name


if __name__ = "__main__":
	usage = "%prog [OPTIONS]... [path_to_solution_xml] [output_ folder]"
	parser = optparse.OptionParser(usage)
	parser.add_option("--build", "-b", action="store", dest="build", default="i686")
	(options, args) = parser.parse_args()

	if len(args) < 2:
		parser.error("Missing required argument.")

	solution = ProjectParser.ParseSolutionAndProjects(args[0]) 
	GenerateMakefiles(solution, args[1], options.build)
