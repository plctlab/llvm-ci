#!/usr/bin/python3
import sys
import json

data_file = sys.argv[1]
revision = sys.argv[2]
url = sys.argv[3]
variant = sys.argv[4]

data = None
with open(data_file) as f:
    data = json.load(f)

data['Machine']['Name'] = variant

info = data['Run']['Info']
info['llvm_revision'] = revision
info['workflow_url'] = url

with open(data_file, 'w') as f:
    json.dump(data, f)
