#!/usr/bin/python3
import subprocess
import os
import sys
import re


def dump_asm(filename: str, objdump):
    with open(filename+'.S', mode="w") as f:
        subprocess.run([objdump, '--no-addresses',
                       '--symbolize-operands', '-S', filename], stdout=f)


def dump_bc(base, dis, count, data):
    filename = "{}/seg{}.bc".format(base, count)
    with open(filename, "wb") as f:
        f.write(data)
    subprocess.run([dis, "seg{}.bc".format(count)], cwd=base)


def diff_ir(out_dir, base1, base2, llvm_diff):
    if not (os.path.exists(base1) and os.path.exists(base2)):
        return

    os.makedirs(out_dir, exist_ok=True)
    diff_file = out_dir+"/diff"
    with open(diff_file, 'w') as diff:
        subprocess.run(['diff', '-x', '"*.bc"', '-q',
                       '-r', base1, base2], stdout=diff)

    pattern = re.compile(r'Files (.+) and (.+) differ')

    diff_count = 0
    with open(diff_file) as diff:
        for line in diff.readlines():
            matched = re.match(pattern, line.removesuffix('\n'))
            if matched is not None:
                lhs = matched.group(1)
                rhs = matched.group(2)
                irdiff_file = out_dir + "/irdiff"+str(diff_count)

                with open(irdiff_file, 'w') as irdiff:
                    irdiff.write(line)
                    irdiff.flush()
                    subprocess.run([llvm_diff, lhs, rhs], stderr=irdiff)

                diff_count += 1


def extract_bc(filename: str, objcopy, dis):
    bc_header = bytes([0x42, 0x43, 0xc0, 0xde])
    basedir = filename+"_bc"
    bc_filename = filename+".bc"

    subprocess.run([objcopy, filename, "--dump-section",
                   ".llvmbc={}".format(bc_filename)])

    if not os.path.exists(bc_filename):
        return

    os.makedirs(basedir, exist_ok=True)

    count = 0

    with open(bc_filename, 'rb') as f:
        data = f.read()

        last_pos = 0
        while True:
            pos = data.find(bc_header, last_pos+4)
            if pos == -1:
                dump_bc(basedir, dis, count, data[last_pos:])
                break
            else:
                dump_bc(basedir, dis, count, data[last_pos: pos])
            last_pos = pos
            count += 1


def check_access(bin):
    return os.path.exists(bin) and os.access(bin, os.X_OK)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage: binutils.py <llvm-bin-path> binary1 binary2')
        exit(1)

    llvm_path = os.path.abspath(sys.argv[1]).removesuffix('/')
    llvm_dis = llvm_path + '/llvm-dis'
    llvm_objdump = llvm_path + "/llvm-objdump"
    llvm_objcopy = llvm_path + "/llvm-objcopy"
    llvm_diff = llvm_path + "/llvm-diff"

    if not (check_access(llvm_dis) and check_access(llvm_objdump) and check_access(llvm_objcopy) and check_access(llvm_diff)):
        print('Error: invalid llvm binaries path')
        exit(1)

    for bin in sys.argv[2:]:
        dump_asm(bin, llvm_objdump)
        extract_bc(bin, llvm_objcopy, llvm_dis)

    diff_ir("irdiff", sys.argv[2]+"_bc", sys.argv[3]+"_bc", llvm_diff)
