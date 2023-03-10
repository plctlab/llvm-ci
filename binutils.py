import subprocess
import os


def dump_asm(filename: str, objdump):
    with open(filename+'.S', mode="w") as f:
        subprocess.run([objdump, '--no-addresses',
                       '--symbolize-operands', '-S', filename], stdout=f)


def dump_bc(base, dis, count, data):
    filename = "{}/seg{}.bc".format(base, count)
    with open(filename, "wb") as f:
        f.write(data)
    subprocess.run([dis, "seg{}.bc".format(count)], cwd=base)


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
