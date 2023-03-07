#!/bin/bash

repo_base=$1

echo "LLVM_REVISION=$(git -C ./llvm-project rev-parse HEAD)" >> $GITHUB_ENV
echo "LLVM_NTS_REVISION=$(git -C ./llvm-test-suite rev-parse HEAD)" >> $GITHUB_ENV

git -C ./llvm-project checkout .
git -C ./llvm-project clean -fdx

$repo_base/setup-pre-commit-patch.sh
rm -f patch
wget https://reviews.llvm.org/$PATCH_ID?download=true -O patch
git -C ./llvm-project apply patch
echo "PATCH_SHA256=$(sha256sum patch)" >> $GITHUB_ENV
echo "PATCH_ADDITIONAL_FLAGS=$PATCH_ADDITIONAL_FLAGS" >> $GITHUB_ENV
echo "PRE_COMMIT_MODE=1" >> $GITHUB_ENV
echo "MODIFIED=1" >> $GITHUB_ENV
echo "FORCE_REBUILD=1" >> $GITHUB_ENV
