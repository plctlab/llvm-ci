#!/bin/bash
set -euo pipefail
shopt -s inherit_errexit

if [ -d "llvm-lnt/.git" ]
then
  cd llvm-lnt
  git checkout .
  git clean -fdx
  git pull
else
  git clone https://github.com/dtcxzyw/llvm-lnt
  cd llvm-lnt
fi
