if __name__ == "__main__":
	print("Hello")

# Process
# 1. Convert from "materials" file that Chroma generates into a bunch of MD files for a Github page
# 2. Convert from a Github page into a "materials" file for Chroma
# 3. Be able to do a lookup: I have X (provides basic merge values) and I want to join to Y (provide ingoing/outgoing values) for a specified printer (or make a request for tests to be done)
# 4. Support error cases and bad mixes (PolyDissolve + ColorFabb works, but any sharp angles or really fast printing could result in the filaments seperating)
# 5. Support filters (AKA, we have filaments A, B, and C... but I only own A and B)
# 6. Support "direct" modification (read and write materials file directly to Chroma folder; support reading/generating files directly from github). Possibly requires data to be serialized for easier management
