#!/usr/bin/python3
import sys
import json

data_file = sys.argv[1]
revision = sys.argv[2]
url = sys.argv[3]

data = None
with open(data_file) as f:
    data = json.load(f)

info = data['Run']['Info']
info['llvm_project_revision'] = revision
info['workflow_url'] = url

with open(data_file, 'w') as f:
    json.dump(data, f)
