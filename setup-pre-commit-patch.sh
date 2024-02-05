#!/bin/bash

#export PATCH_ID=DXXXXXX
export GITHUB_PATCH_ID="llvm/llvm-project/pull/78417"
export PATCH_ADDITIONAL_FLAGS=" -Xclang -target-feature -Xclang +no-ret-addr-stack "
