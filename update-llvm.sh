#!/bin/bash
set -euo pipefail
shopt -s inherit_errexit

if [ -d "llvm-project/.git" ]
then
  cd llvm-project
  git checkout .
  git clean -fdx
  if [ -r llvm_revision ]
  then
    last_commit=$(cat llvm_revision)
  else
    last_commit=$(git rev-parse HEAD)
  fi
  
  git pull
  current_commit=$(git rev-parse HEAD)
  echo -e "from $last_commit to $current_commit\n" > ../artifacts/CHANGELOGS
  git log $last_commit..HEAD --pretty=oneline >> ../artifacts/CHANGELOGS
  cat ../artifacts/CHANGELOGS
  if [ $last_commit = $current_commit ]
  then
    echo "No changes"
    export MODIFIED=0
  else
    echo "Modified"
    export MODIFIED=1
  fi
  echo "MODIFIED=$MODIFIED" >> $GITHUB_ENV
else
  git clone https://github.com/llvm/llvm-project
fi
