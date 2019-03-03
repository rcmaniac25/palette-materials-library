import yaml

# dict has some different values between python 2 and 3, so helper utils for now
def util_dict_items(d):
	# https://stackoverflow.com/a/3294899/492347
	return d.items()

def util_dict_values(d):
	# https://stackoverflow.com/a/3294899/492347 (see the responses below the link)
	return d.values()

def get_chroma_materials_path():
	#TODO
	path = "C:/Users/{0}/AppData/Roaming/Chroma/materials-2.yml"
	user = "<todo>"
	return path.format(user)

def has_settings(mat, typ):
	for combo in util_dict_values(mat["combinations"]):
		if combo["spliceCore"] == typ:
			if combo["heatFactor"] != 0 and combo["compressionFactor"] != 0:
				return True
	return False

if __name__ == "__main__":
	path = get_chroma_materials_path()
	with open(path) as mat_file:
		materials = yaml.load(mat_file)

	palette_type = "P" # Palette/Palette+
	if materials["version"] != 2:
		print("WARNING: Code written against version 2 of the materials file. Found version {0} which may have a different format".format(materials["version"]))

	material_names = []
	for mat_key, mat_val in util_dict_items(materials["matrix"][palette_type]):
		if has_settings(mat_val, palette_type):
			material_names.append(mat_key)

	# m1 == m2 : only one set of values
	# m1[combo][m2] : m1 = ingo, m2 = outgo
	# m2[combo][m1] : m1 = outgo, m2 = ingo

	print(material_names)

# Process
# 1. Convert from "materials" file that Chroma generates into a bunch of MD files for a Github page
# 2. Convert from a Github page into a "materials" file for Chroma
# 3. Be able to do a lookup: I have X (provides basic merge values) and I want to join to Y (provide ingoing/outgoing values) for a specified printer (or make a request for tests to be done)
# 4. Support error cases and bad mixes (PolyDissolve + ColorFabb works, but any sharp angles or really fast printing could result in the filaments seperating)
# 5. Support filters (AKA, we have filaments A, B, and C... but I only own A and B)
# 6. Support "direct" modification (read and write materials file directly to Chroma folder; support reading/generating files directly from github). Possibly requires data to be serialized for easier management
