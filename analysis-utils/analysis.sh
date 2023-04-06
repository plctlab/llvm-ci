#!/bin/bash
set -eo pipefail
shopt -s inherit_errexit

variant=$1
hash_baseline=$2
hash_regression=$3

rm -rf analysis
mkdir analysis
cd analysis
cp ~/llvm-ci/$variant/binaries/$hash_baseline baseline
cp ~/llvm-ci/$variant/binaries/$hash_regression regression
python3 ~/WorkSpace/llvm-ci/binutils.py ~/llvm-ci/$variant/llvm-build/bin baseline regression
python3 ~/WorkSpace/llvm-ci/analysis-utils/asm_diff.py baseline.S regression.S
