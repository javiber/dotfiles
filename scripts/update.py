#!/usr/bin/env python

import json

from os.path import expanduser
from shutil import copyfile

with open("file_map.json") as f:
    file_map = json.load(f)

for local, remote in file_map.items():
    print "updating {}".format(local)
    copyfile(expanduser(remote), local)
