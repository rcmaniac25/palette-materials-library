import yaml

import platform
import os
import sys
import shutil

is_python_3 = sys.version_info[0] == 3
root_docs_path = "./docs"

# dict has some different values between python 2 and 3, so helper utils for now
def util_dict_items(d):
	# https://stackoverflow.com/a/3294899/492347
	if is_python_3: return d.items()
	else: return d.iteritems()

def util_dict_values(d):
	# https://stackoverflow.com/a/3294899/492347 (see the responses below the link)
	if is_python_3: return d.values()
	else: return d.itervalues()

def util_dict_keys(d):
	# https://stackoverflow.com/a/3294899/492347 (see the responses below the link)
	if is_python_3: return d.keys()
	else: return d.iterkeys()

def get_chroma_materials_path():
	if platform.system() == "Windows":
		# <drive>\Users\<username>\AppData\Roaming\Chroma
		appdata = os.getenv("APPDATA")
		path = "{0}\\Chroma\\materials-2.yml".format(appdata)
	elif platform.system() == "Darwin":
		#<home folder>/Library/Application Support/Chroma
		home = os.path.expanduser("~")
		path = "{0}/Library/Application Support/Chroma/materials-2.yml".format(home)
	else:
		#TODO
		path = "TODO"
	return path

def has_settings(mat, typ):
	for combo in util_dict_values(mat["combinations"]):
		if combo["spliceCore"] == typ:
			if combo["heatFactor"] != 0 and combo["compressionFactor"] != 0:
				return True
	return False

def get_palette_type_name_mod(typ):
	# Expects this is being used with the format "Palette{get_palette_type_name_mod(type)}"
	if typ == "P":
		return "/Palette+"
	elif typ == "SC":
		return " 2"
	elif typ == "SCP":
		return " 2 Pro"
	return "<unknown typ {0}>".format(typ)

def get_palette_type_folder(typ):
	if typ == "P":
		return "palette1"
	elif typ == "SC":
		return " palette2"
	elif typ == "SCP":
		return " palette2pro"
	return typ

def print_row(mat_merge_key, mat_merge_value, mat_merge_value_reverse, mat_gen, typ, file):
	# m1 == m2 : only one set of values
	# m1[combo][m2] : m1 = ingo, m2 = outgo
	# m2[combo][m1] : m1 = outgo, m2 = ingo

	def print_P(key, value):
		file.write("{0} | Heat Factor: {1}, Compression Factor: {2}, Reverse Splicing: {3}\n".format(key, value["heatFactor"], value["compressionFactor"], value["reverse"]))

	def print_SCx(key, value):
		file.write("{0} | Heat Factor: {1}, Compression Factor: {2}, Cooling Factor: {3}, Reverse Splicing: {4}\n".format(key, value["heatFactor"], value["compressionFactor"], value["coolingFactor"], value["reverse"]))

	def print_self():
		if typ == "P":
			print_P(mat_merge_key, mat_merge_value)
		else:
			print_SCx(mat_merge_key, mat_merge_value)

	def print_other():
		combo1 = "{0} (ingoing) to {1} (outgoing)".format(mat_gen, mat_merge_key)
		combo2 = "{0} (ingoing) to {1} (outgoing)".format(mat_merge_key, mat_gen)
		do_combo2 = mat_merge_value_reverse["heatFactor"] != 0 and mat_merge_value_reverse["compressionFactor"] != 0

		if typ == "P":
			print_P(combo1, mat_merge_value)
			if do_combo2: print_P(combo2, mat_merge_value_reverse)
		else:
			print_SCx(combo1, mat_merge_value)
			if do_combo2: print_SCx(combo2, mat_merge_value_reverse)

	if mat_merge_value["heatFactor"] != 0 and mat_merge_value["compressionFactor"] != 0:
		if mat_merge_key == mat_gen:
			print_self()
		else:
			print_other()

def print_for_palette_type(materials, palette_type):
	material_names = []
	for mat_key, mat_val in util_dict_items(materials["matrix"][palette_type]):
		if has_settings(mat_val, palette_type):
			material_names.append(mat_key)

	for mat_for_gen in material_names:
		filename = mat_for_gen.lower().replace(" ", "_")
		path = os.path.join(root_docs_path, get_palette_type_folder(palette_type), "{0}.md".format(filename))
		with open(path, "w") as doc_file:
			doc_file.write("# {0}\n\nFor Palette{1}\n\n".format(mat_for_gen, get_palette_type_name_mod(palette_type)))

			doc_file.write("## Splices\n\nMaterial | Values\n-------- | ------\n")
			for mat_for_merg in material_names:
				mat_for_merg_value = materials["matrix"][palette_type][mat_for_gen]["combinations"][mat_for_merg] # mat_for_gen = ingo, mat_for_merg = outgo
				mat_for_merg_value_reversed = materials["matrix"][palette_type][mat_for_merg]["combinations"][mat_for_gen] # mat_for_gen = outgo, mat_for_merg = ingo

				print_row(mat_for_merg, mat_for_merg_value, mat_for_merg_value_reversed, mat_for_gen, palette_type, doc_file)

			doc_file.write("\n")
			doc_file.flush()

if __name__ == "__main__":
	print("Starting")

	path = get_chroma_materials_path()
	print("Reading Chroma materials file from {0}".format(path))
	with open(path) as mat_file:
		materials = yaml.load(mat_file)

	palette_type = "P" # Palette/Palette+
	if materials["version"] != 2:
		print("WARNING: Code written against version 2 of the materials file. Found version {0} which may have a different format".format(materials["version"]))

	print("Preparing folders")
	if not os.path.isdir(root_docs_path):
		os.mkdir(root_docs_path)
	path = os.path.normpath(os.path.join(root_docs_path, get_palette_type_folder(palette_type)))
	if os.path.isdir(path):
		shutil.rmtree(path)
	os.mkdir(path)

	print("Writing material documents")
	print_for_palette_type(materials, palette_type)

	print("Finished")

# Process
# 1. Convert from "materials" file that Chroma generates into a bunch of MD files for a Github page
# 2. Convert from a Github page into a "materials" file for Chroma
# 3. Be able to do a lookup: I have X (provides basic merge values) and I want to join to Y (provide ingoing/outgoing values) for a specified printer (or make a request for tests to be done)
# 4. Support error cases and bad mixes (PolyDissolve + ColorFabb works, but any sharp angles or really fast printing could result in the filaments seperating)
# 5. Support filters (AKA, we have filaments A, B, and C... but I only own A and B)
# 6. Support "direct" modification (read and write materials file directly to Chroma folder; support reading/generating files directly from github). Possibly requires data to be serialized for easier management
