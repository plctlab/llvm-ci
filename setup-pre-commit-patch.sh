#!/bin/bash

export PATCH_ID=D148216 # This is an NFC patch
#export GITHUB_PATCH_ID="<user_name>/llvm-project/commit/<commit_hash>"
export PATCH_ADDITIONAL_FLAGS=" -mllvm -enable-newgvn"
