#!/usr/bin/python3
import sys
import json
import os
import shutil
import html
import datetime
import statistics

lhs = sys.argv[1]
rhs = sys.argv[2]
base_dir = sys.argv[3]
workflow_url = sys.argv[4]
binaries_src = base_dir+"/binaries/"
binaries_dst = base_dir+"/artifacts/binaries/"
os.makedirs(binaries_dst)

threshold_abs = 16
threshold_rel = 1.001
limit = 20


def parse(path):
    res = dict()
    with open(path, "r", encoding='utf-8') as f:
        data = json.load(f)
        tests = data['tests']
        for test in tests:
            name = test['name']
            metrics = test['metrics']
            size = metrics['size..text']
            if size > 0:
                res[name] = (metrics['hash'], size)
    return res


def copy_binary(lhs, rhs):
    if os.path.exists(lhs):
        shutil.copyfile(lhs, rhs)


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


def dump_diff(report, lhs_data, rhs_data, copy_binaries):
    report.write('## Differences\n')
    report.write(
        '|Name|Baseline MD5|Current MD5|Baseline Size|Current Size|Ratio|\n')
    report.write('|:--|:--:|:--:|--:|--:|--:|\n')

    diff_list = []
    lhs_list = []
    rhs_list = []
    for name in lhs_data.keys():
        if name in rhs_data:
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

    for name, lhs_hash, rhs_hash, lhs_size, rhs_size in diff_list:
        report.write("|{}|{}|{}|{}|{}|{:.3f}|\n".format(
            strip_name(name), lhs_hash, rhs_hash, lhs_size, rhs_size, rhs_size/lhs_size))
        if copy_binaries:
            copy_binary(binaries_src+lhs_hash, binaries_dst+lhs_hash)
            copy_binary(binaries_src+rhs_hash, binaries_dst+rhs_hash)

    if len(lhs_list) > 0:
        gmean_lhs = statistics.geometric_mean(lhs_list)
        gmean_rhs = statistics.geometric_mean(rhs_list)
        report.write("|GeoMeans|N/A|N/A|{:.3f}|{:.3f}|{:.3f}|\n".format(
                     gmean_lhs, gmean_rhs, gmean_rhs/gmean_lhs))


lhs_data = parse(lhs)
rhs_data = parse(rhs)

if 'PRE_COMMIT_MODE' in os.environ:
    pr_comment_path = base_dir+"/artifacts/pr-comment_generated.md"
    with open(pr_comment_path, "w") as pr_comment:
        pr_comment.write('## Metadata\n')
        pr_comment.write('+ Workflow URL: {}\n'.format(workflow_url))
        pr_comment.write(
            '+ LLVM revision: {}\n'.format(os.environ['LLVM_REVISION']))
        pr_comment.write(
            '+ LLVM Test Suite revision: {}\n'.format(os.environ['LLVM_NTS_REVISION']))
        pr_comment.write(
            '+ Patch SHA256: {}\n'.format(os.environ['PATCH_SHA256']))

        dump_diff(pr_comment, lhs_data, rhs_data, True)
else:
    binary_bloating_list = []
    for name in lhs_data.keys():
        if name in rhs_data:
            lhs_hash, lhs_value = lhs_data[name]
            rhs_hash, rhs_value = rhs_data[name]

            if lhs_value * threshold_rel < rhs_value or lhs_value + threshold_abs < rhs_value:
                binary_bloating_list.append(
                    (name, lhs_hash, rhs_hash, lhs_value, rhs_value))

    if len(binary_bloating_list) == 0:
        print("No regressions")
        exit(0)

    else:
        change_logs_path = base_dir+"/artifacts/CHANGELOGS"
        issue_report_path = base_dir+"/artifacts/issue_generated.md"
        with open(issue_report_path, "w") as issue_report:
            issue_report.write('---\n')
            issue_report.write(
                "title: Size Regressions Report {{ date | date('MMMM Do YYYY, h:mm:ss a') }}\n")
            issue_report.write('labels: regression\n')
            issue_report.write('---\n')
            issue_report.write('## Metadata\n')
            issue_report.write('+ Workflow URL: {}\n'.format(workflow_url))

            dump_pretty_change_logs(issue_report, change_logs_path)

            issue_report.write('## Regressions\n')
            issue_report.write(
                '|Name|Baseline MD5|Current MD5|Baseline Size|Current Size|Ratio|\n')
            issue_report.write('|:--|:--:|:--:|--:|--:|--:|\n')

            binary_bloating_list.sort(key=lambda x: x[4]/x[3], reverse=True)
            if len(binary_bloating_list) > limit:
                binary_bloating_list = binary_bloating_list[:limit]

            for name, lhs_hash, rhs_hash, lhs_size, rhs_size in binary_bloating_list:
                issue_report.write("|{}|{}|{}|{}|{}|{:.3f}|\n".format(strip_name(name), lhs_hash,
                                                                      rhs_hash, lhs_size, rhs_size, rhs_size/lhs_size))
                copy_binary(binaries_src+lhs_hash, binaries_dst+lhs_hash)
                copy_binary(binaries_src+rhs_hash, binaries_dst+rhs_hash)

            dump_diff(issue_report, lhs_data, rhs_data, False)

        exit(1)
