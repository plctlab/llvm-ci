#!/usr/bin/python3
import sys
import json
import os
import shutil
import html
import datetime

lhs = sys.argv[1]
rhs = sys.argv[2]
base_dir = sys.argv[3]
workflow_url = sys.argv[4]

threshold_abs = 16
threshold_rel = 1.001


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


def dump_pretty_change_logs(issue_report, change_logs_path):
    with open(change_logs_path, "r") as change_logs:
        for line in change_logs.readlines():
            if len(line) > 40 and line[:40].isalnum() and not line.startswith('from'):
                commit_id = line[:40]
                remain = line[40:]
                issue_report.write(
                    "[{0}](https://github.com/llvm/llvm-project/commit/{0}){1}\n".format(commit_id, html.escape(remain.removesuffix('\n'))))
            else:
                issue_report.write(line)


def strip_name(name: str):
    return name.removeprefix(
        'test-suite :: ').removesuffix('.test')


lhs_data = parse(lhs)
rhs_data = parse(rhs)

binary_bloating_list = []

for name in lhs_data.keys():
    if name in rhs_data:
        lhs_hash, lhs_value = lhs_data[name]
        rhs_hash, rhs_value = rhs_data[name]

        if lhs_value * threshold_rel < rhs_value or lhs_value + threshold_abs < rhs_value:
            binary_bloating_list.append(
                (name, lhs_hash, rhs_hash, lhs_value, rhs_value))

change_logs_path = base_dir+"/artifacts/CHANGELOGS"
issue_report_path = base_dir+"/artifacts/issue_generated.md"

if len(binary_bloating_list) == 0:
    with open(issue_report_path, "w") as issue_report:
        issue_report.write('---\n')
        issue_report.write("title: Nightly Build Summary\n")
        issue_report.write('---\n')
        issue_report.write('## Metadata\n')
        issue_report.write('+ workflow url: {}\n'.format(workflow_url))
        current = datetime.datetime.now()
        issue_report.write(
            '+ timestamp: {}\n'.format(current.strftime("%Y-%m-%d %H:%M:%S")))
        issue_report.write('## Change Logs\n')

        dump_pretty_change_logs(issue_report, change_logs_path)

        issue_report.write('## Differences\n')
        issue_report.write(
            '|Name|Baseline Size|Current Size|Ratio|\n')
        issue_report.write('|:--|--:|--:|--:|\n')

        diff_list = []
        for name in lhs_data.keys():
            if name in rhs_data:
                lhs_hash, lhs_value = lhs_data[name]
                rhs_hash, rhs_value = rhs_data[name]

                if lhs_value != rhs_value:
                    diff_list.append(
                        (name, lhs_value, rhs_value))

        diff_list.sort(key=lambda x: x[2]/x[1], reverse=True)
        for name, lhs_size, rhs_size in binary_bloating_list:
            issue_report.write("|{}|{}|{}|{:.3f}|\n".format(
                strip_name(name), lhs_size, rhs_size, rhs_size/lhs_size))

    print("No regressions")

else:
    with open(issue_report_path, "w") as issue_report:
        issue_report.write('---\n')
        issue_report.write(
            "title: Size Regressions Report {{ date | date('MMMM Do YYYY, h:mm:ss a') }}\n")
        issue_report.write('labels: regression\n')
        issue_report.write('---\n')
        issue_report.write('## Metadata\n')
        issue_report.write('+ workflow url: {}\n'.format(workflow_url))
        issue_report.write('## Change Logs\n')

        dump_pretty_change_logs(issue_report, change_logs_path)

        issue_report.write('## Regressions\n')
        issue_report.write(
            '|Name|Baseline MD5|Current MD5|Baseline Size|Current Size|Ratio|\n')
        issue_report.write('|:--|:--:|:--:|--:|--:|--:|\n')

        binaries_src = base_dir+"/binaries/"
        binaries_dst = base_dir+"/artifacts/binaries/"
        os.makedirs(binaries_dst)

        binary_bloating_list.sort(key=lambda x: x[4]/x[3], reverse=True)

        for name, lhs_hash, rhs_hash, lhs_size, rhs_size in binary_bloating_list:
            issue_report.write("|{}|{}|{}|{}|{}|{:.3f}|\n".format(strip_name(name), lhs_hash,
                                                                  rhs_hash, lhs_size, rhs_size, rhs_size/lhs_size))
            copy_binary(binaries_src+lhs_hash, binaries_dst+lhs_hash)
            copy_binary(binaries_src+rhs_hash, binaries_dst+rhs_hash)
