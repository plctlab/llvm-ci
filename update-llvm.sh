#!/bin/bash

if [ -d "llvm-project/.git" ]
then
  cd llvm-project
  git checkout .
  git clean -fdx
  last_commit=$(git rev-parse HEAD)
  git pull
  current_commit=$(git rev-parse HEAD)
  echo -e "from $last_commit to $current_commit\n" > ../CHANGELOGS
  git log $last_commit..HEAD --pretty=oneline >> ../CHANGELOGS
else
  git clone https://github.com/llvm/llvm-project
fi

# TODO: apply patches
