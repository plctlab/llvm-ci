#!/bin/bash

if [ -d "llvm-project/.git" ]
then
  cd llvm-project
  git checkout .
  git clean -fdx
  git pull
else
  git clone https://github.com/llvm/llvm-project
fi

# TODO: update commit id
# TODO: apply patches
