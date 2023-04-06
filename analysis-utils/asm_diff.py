#!/usr/bin/python3
import sys
import os

file1 = sys.argv[1]
file2 = sys.argv[2]


def split(filename: str):
    dir_name = filename.removesuffix('.S')+"_S"

    with open(filename) as f:
        os.makedirs(dir_name, exist_ok=True)
        name = None
        content = []
        for line in f.readlines():
            if line.startswith('<') and line.endswith('>:\n'):
                if name:
                    if len(name) > 32:
                        name = name[:32]
                    with open(dir_name+"/"+name, 'w') as out:
                        out.writelines(content)

                name = line[1:-3]
                content.clear()
            elif len(line) > 25:
                sub = line[24:]
                inst = sub[:sub.find('\t')]
                content.append(inst+'\n')

    return dir_name


dir1 = split(file1)
dir2 = split(file2)
os.system("diff -r -q {} {}".format(dir1, dir2))
