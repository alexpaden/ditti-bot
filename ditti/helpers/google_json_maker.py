import base64
import json
import os


def run_google_maker():
    coded = os.getenv("GOOGLE_B64", "VALUE NOT SET")
    decoded = base64.standard_b64decode(coded)

    json_object = json.loads(decoded)

    outfile = open("google_credentials.json", "w")

    json.dump(json_object, outfile)

    outfile.close()
