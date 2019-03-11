import yaml

import platform
import os
import sys
import shutil

is_python_3 = sys.version_info[0] == 3
md_root_docs_path = "docs"
os_root_docs_path = "./{0}".format(md_root_docs_path)
palette_materials_file = "palette.md"

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

def correct_path(path, for_web=False):
	if for_web:
		return path.replace('\\', '/')
	return path

def generate_material_file(material):
	return "{0}.md".format(material.lower().replace(" ", "_"))

def generate_material_path(palette_type, root, for_web=False):
	return correct_path(os.path.join(root, get_palette_type_folder(palette_type)), for_web)

def generate_material_file_path(material, palette_type, root, for_web=False):
	filename = material.lower().replace(" ", "_")
	return correct_path(os.path.join(generate_material_path(palette_type, root), generate_material_file(material)), for_web)

def generate_palette_file_path(palette_type, root, for_web=False):
	return correct_path(os.path.join(generate_material_path(palette_type, root), palette_materials_file), for_web)

def print_row(mat_merge_key, mat_merge_value, mat_merge_value_reverse, mat_gen, typ, file):
	# m1 == m2 : only one set of values
	# m1[combo][m2] : m1 = ingo, m2 = outgo
	# m2[combo][m1] : m1 = outgo, m2 = ingo

	def print_P(key, value):
		file.write("{0} | **Heat Factor**: {1}, **Compression Factor**: {2}, **Reverse Splicing**: {3}\n".format(key, value["heatFactor"], value["compressionFactor"], value["reverse"]))

	def print_SCx(key, value):
		file.write("{0} | **Heat Factor**: {1}, **Compression Factor**: {2}, **Cooling Factor**: {3}, **Reverse Splicing**: {4}\n".format(key, value["heatFactor"], value["compressionFactor"], value["coolingFactor"], value["reverse"]))

	def print_self():
		if typ == "P":
			print_P("_{0}_".format(mat_merge_key), mat_merge_value)
		else:
			print_SCx("_{0}_".format(mat_merge_key), mat_merge_value)

	def print_other():
		mat_gen_file = generate_material_file(mat_merge_key)
		combo1 = "_{0}_ (ingoing) to [{1}]({2}) (outgoing)".format(mat_gen, mat_merge_key, mat_gen_file)
		combo2 = "[{0}]({1}) (ingoing) to _{2}_ (outgoing)".format(mat_merge_key, mat_gen_file, mat_gen)
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
		path = generate_material_file_path(mat_for_gen, palette_type, os_root_docs_path)
		with open(path, "w") as doc_file:
			doc_file.write("# {0}\n\nFor [Palette{1}]({2})\n\n".format(mat_for_gen, get_palette_type_name_mod(palette_type), palette_materials_file))

			doc_file.write("## Splices\n\nMaterial | Values\n-------- | ------\n")
			for mat_for_merg in material_names:
				mat_for_merg_value = materials["matrix"][palette_type][mat_for_gen]["combinations"][mat_for_merg] # mat_for_gen = ingo, mat_for_merg = outgo
				mat_for_merg_value_reversed = materials["matrix"][palette_type][mat_for_merg]["combinations"][mat_for_gen] # mat_for_gen = outgo, mat_for_merg = ingo

				print_row(mat_for_merg, mat_for_merg_value, mat_for_merg_value_reversed, mat_for_gen, palette_type, doc_file)

			doc_file.flush()

		path = generate_palette_file_path(palette_type, os_root_docs_path)
		with open(path, "a") as palette_doc:
			file = generate_material_file(mat_for_gen)
			palette_doc.write(" - [{0}]({1})\n".format(mat_for_gen, file))

def define_root_docs(palette_type):
	# Materials Splices
	path = os.path.join(os_root_docs_path, "material_splices.md")
	if os.path.exists(path):
		os.remove(path)

	with open(path, "w") as splice_doc:
		splice_doc.write("# Material Splices\n\nKnown Palettes:\n\n - [Palette{0}]({1})\n".format(get_palette_type_name_mod(palette_type), generate_palette_file_path(palette_type, "", for_web=True)))

	# Palette-specific (to be appended to)
	path = generate_palette_file_path(palette_type, os_root_docs_path)
	if os.path.exists(path):
		os.remove(path)

	with open(path, "w") as palette_doc:
		palette_doc.write("# Palette{0} Material Splices\n\n## Materials\n\n".format(get_palette_type_name_mod(palette_type)))

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
	if not os.path.isdir(os_root_docs_path):
		os.mkdir(os_root_docs_path)
	path = os.path.normpath(os.path.join(os_root_docs_path, get_palette_type_folder(palette_type)))
	if os.path.isdir(path):
		shutil.rmtree(path)
	os.mkdir(path)

	print("Preparing root documents")
	define_root_docs(palette_type)

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
