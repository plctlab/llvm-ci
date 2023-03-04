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
    echo "No changes"
    export MODIFIED=0
    echo "MODIFIED=0" >> $GITHUB_ENV
  else
    echo "Modified"
    export MODIFIED=1
    echo "MODIFIED=1" >> $GITHUB_ENV
  fi
else
  git clone https://github.com/llvm/llvm-project
fi

# TODO: apply patches
