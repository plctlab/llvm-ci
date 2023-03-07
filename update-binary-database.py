#!/usr/bin/python3
import sys
import shutil
import hashlib
import pathlib
import os

src = sys.argv[1]
dst = sys.argv[2]

cnt = 0
for r, ds, fs in os.walk(src):
    for f in fs:
        path = r + '/' + f
        if os.access(path, os.X_OK) and f.endswith(".stripped"):
            dst_path = None
            with open(path, "rb") as file:
                dst_path = dst + "/" + \
                    str(hashlib.md5(file.read()).hexdigest())
            if not os.path.exists(dst_path):
                print("new binary", path.removesuffix(".stripped"), '->', dst_path)
                shutil.copyfile(path, dst_path)
                cnt += 1
            else:
                pathlib.Path(dst_path).touch()
print(cnt, "file(s) updated")
