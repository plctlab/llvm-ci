#!/bin/bash

if [ -d "llvm-project/.git" ]
then
  cd llvm-project
  git checkout .
  git clean -fdx
  last_commit=$(git rev-parse HEAD)
  git pull
  current_commit=$(git rev-parse HEAD)
  echo -e "from $last_commit to $current_commit\n" > ../artifacts/CHANGELOGS
  git log $last_commit..HEAD --pretty=oneline >> ../artifacts/CHANGELOGS
  cat ../artifacts/CHANGELOGS
  if [ $last_commit = $current_commit ]
  then
    export UNCHANGED=1
    echo "UNCHANGED=1" >> $GITHUB_ENV
  fi
else
  git clone https://github.com/llvm/llvm-project
fi

# TODO: apply patches
