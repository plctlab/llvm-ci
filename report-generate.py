#!/usr/bin/python3
import sys
import json
import os
import shutil
import html
import datetime
import statistics
import binutils

lhs = sys.argv[1]
rhs = sys.argv[2]
base_dir = sys.argv[3]
workflow_url = sys.argv[4]
variant = sys.argv[5]
binaries_src = base_dir+"/binaries/"
binaries_dst = base_dir+"/artifacts/binaries/"
llvm_path = base_dir+"/llvm-build/bin/"
os.makedirs(binaries_dst)

limit = 20


def strip_subtest(name: str):
    pos = name.find('.test:')
    if pos == -1:
        return name
    return name[:pos+5]


def parse_result(path):
    res_binary = dict()
    res_time = dict()
    with open(path, "r", encoding='utf-8') as f:
        data = json.load(f)
        tests = data['tests']
        for test in tests:
            if 'name' not in test or 'metrics' not in test:
                continue
            name = test['name']
            metrics = test['metrics']
            if test['code'] != 'PASS':
                continue
            if 'size' not in metrics:
                continue
            size = metrics['size..text']
            if size > 0:
                res_binary[name] = (metrics['hash'], size)
        for test in tests:
            if 'name' not in test or 'metrics' not in test:
                continue
            name = test['name']
            metrics = test['metrics']
            if test['code'] != 'PASS':
                continue
            if 'exec_time' not in metrics:
                continue
            hash_value = None
            if 'hash' in metrics:
                hash_value = metrics['hash']
            else:
                hash_value = res_binary[strip_subtest(name)][0]
            res_time[name] = (hash_value, metrics['exec_time'])
    return res_binary, res_time


def copy_binary(lhs, rhs):
    if os.path.exists(lhs):
        shutil.copyfile(lhs, rhs)
        binutils.dump_asm(rhs, os.path.abspath(llvm_path+"llvm-objdump"))
        binutils.extract_bc(rhs, os.path.abspath(llvm_path+"llvm-objcopy"),
                            os.path.abspath(llvm_path+"llvm-dis"))


def dump_pretty_change_logs(report, change_logs_path):
    report.write('## Change Logs\n')

    with open(change_logs_path, "r") as change_logs:
        for line in change_logs.readlines():
            if len(line) > 40 and line[:40].isalnum() and not line.startswith('from'):
                commit_id = line[:40]
                remain = line[40:]
                report.write(
                    "[{0}](https://github.com/llvm/llvm-project/commit/{0}){1}\n".format(commit_id, html.escape(remain.removesuffix('\n'))))
            else:
                report.write(line)


def strip_name(name: str):
    return name.removeprefix(
        'test-suite :: ').removesuffix('.test')


def dump_diff(report, lhs_data, rhs_data, metric, compare_pairs: set):
    report.write('## Differences ({})\n'.format(metric))
    report.write(
        '|Name|Baseline MD5|Current MD5|Baseline {}|Current {}|Ratio|\n'.format(metric, metric))
    report.write('|:--|:--:|:--:|--:|--:|--:|\n')

    diff_list = []
    lhs_list = []
    rhs_list = []
    for name in lhs_data.keys():
        if name in rhs_data:
            if metric == 'Time' and str(name).startswith('test-suite :: MicroBenchmarks') and str(name).endswith(".test"):
                continue

            lhs_hash, lhs_value = lhs_data[name]
            rhs_hash, rhs_value = rhs_data[name]

            if lhs_hash != rhs_hash:
                if lhs_value != rhs_value:
                    lhs_list.append(lhs_value)
                    rhs_list.append(rhs_value)
                diff_list.append(
                    (name, lhs_hash, rhs_hash, lhs_value, rhs_value))

    diff_list.sort(key=lambda x: x[4]/x[3], reverse=True)
    if len(diff_list) > limit*2:
        first = diff_list[:limit]
        last = diff_list[-limit:]
        diff_list = first
        diff_list.extend(last)

    for name, lhs_hash, rhs_hash, lhs_value, rhs_value in diff_list:
        report.write("|{}|{}|{}|{}|{}|{:.3f}|\n".format(
            strip_name(name), lhs_hash, rhs_hash, lhs_value, rhs_value, rhs_value/lhs_value))
        compare_pairs.add((lhs_hash, rhs_hash))

    if len(lhs_list) > 0:
        gmean_lhs = statistics.geometric_mean(lhs_list)
        gmean_rhs = statistics.geometric_mean(rhs_list)
        report.write("|GeoMeans|N/A|N/A|{:.3f}|{:.3f}|{:.3f}|\n".format(
                     gmean_lhs, gmean_rhs, gmean_rhs/gmean_lhs))


def compare_binary(compare_pairs: set):
    for lhs_hash, rhs_hash in compare_pairs:
        copy_binary(binaries_src+lhs_hash, binaries_dst+lhs_hash)
        copy_binary(binaries_src+rhs_hash, binaries_dst+rhs_hash)
        binutils.diff_ir(binaries_dst+'irdiff-{}-{}'.format(lhs_hash, rhs_hash), binaries_dst +
                         lhs_hash+"_bc", binaries_dst+rhs_hash+"_bc", os.path.abspath(llvm_path+"llvm-diff"))


def dump_regressions(report, lhs_data, rhs_data, metric, threshold_rel, threshold_abs):
    regressions = []
    for name in lhs_data.keys():
        if name in rhs_data:
            lhs_hash, lhs_value = lhs_data[name]
            rhs_hash, rhs_value = rhs_data[name]

            if lhs_hash == rhs_hash:
                continue

            if metric == 'Time' and str(name).startswith('test-suite :: MicroBenchmarks') and str(name).endswith(".test"):
                continue

            rel_regression = lhs_value * threshold_rel < rhs_value
            #abs_regression = lhs_value + threshold_abs < rhs_value
            abs_regression = False

            if rel_regression or (str(name).endswith(".test") and abs_regression):
                regressions.append(
                    (name, lhs_hash, rhs_hash, lhs_value, rhs_value))

    if len(regressions) == 0:
        return False

    report.write('## Regressions ({})\n'.format(metric))
    report.write(
        '|Name|Baseline MD5|Current MD5|Baseline {}|Current {}|Ratio|\n'.format(metric, metric))
    report.write('|:--|:--:|:--:|--:|--:|--:|\n')

    regressions.sort(key=lambda x: x[4]/x[3], reverse=True)
    if len(regressions) > limit:
        regressions = regressions[:limit]

    for name, lhs_hash, rhs_hash, lhs_value, rhs_value in regressions:
        report.write("|{}|{}|{}|{}|{}|{:.3f}|\n".format(strip_name(name), lhs_hash,
                                                        rhs_hash, lhs_value, rhs_value, rhs_value/lhs_value))
    return True


lhs_bin, lhs_time = parse_result(lhs)
rhs_bin, rhs_time = parse_result(rhs)
compare_pairs = set()

if 'PRE_COMMIT_MODE' in os.environ:
    pr_comment_path = base_dir+"/artifacts/pr-comment_generated.md"
    with open(pr_comment_path, "w") as pr_comment:
        pr_comment.write('## Metadata\n')
        pr_comment.write('+ Workflow URL: {}\n'.format(workflow_url))
        pr_comment.write('+ Variant: {}\n'.format(variant))
        pr_comment.write(
            '+ LLVM revision: {}\n'.format(os.environ['LLVM_REVISION']))
        pr_comment.write(
            '+ LLVM Test Suite revision: {}\n'.format(os.environ['LLVM_NTS_REVISION']))
        pr_comment.write(
            '+ Patch URL: {}\n'.format(os.environ['PATCH_URL']))
        pr_comment.write(
            '+ Patch SHA256: {}\n'.format(os.environ['PATCH_SHA256']))

        dump_diff(pr_comment, lhs_bin, rhs_bin, 'Size', compare_pairs)
        dump_diff(pr_comment, lhs_time, rhs_time, 'Time', compare_pairs)
        compare_binary(compare_pairs)
else:
    change_logs_path = base_dir+"/artifacts/CHANGELOGS"
    issue_report_path = base_dir+"/artifacts/issue_generated.md"
    with open(issue_report_path, "w") as issue_report:
        issue_report.write('---\n')
        issue_report.write(
            "title: Regressions Report ["+variant+"] {{ date | date('MMMM Do YYYY, h:mm:ss a') }}\n")
        issue_report.write('labels: regression\n')
        issue_report.write('---\n')
        issue_report.write('## Metadata\n')
        issue_report.write('+ Workflow URL: {}\n'.format(workflow_url))

        dump_pretty_change_logs(issue_report, change_logs_path)

        r1 = dump_regressions(issue_report, lhs_bin,
                              rhs_bin, 'Size', 1.05, 16)
        r2 = dump_regressions(issue_report, lhs_time, rhs_time,
                              'Time', 1.05, 1e-6)  # ~1000 instructions

        dump_diff(issue_report, lhs_bin, rhs_bin, 'Size', compare_pairs)
        dump_diff(issue_report, lhs_time, rhs_time, 'Time', compare_pairs)
        compare_binary(compare_pairs)

    if r1 or r2:
        exit(1)
    else:
        print("No regressions")
        exit(0)
