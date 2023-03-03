#!/bin/bash

mkdir -p llvm-build
cd llvm-build
cmake ../llvm-project/llvm -DCMAKE_BUILD_TYPE=Release -G Ninja \
        -DLLVM_ENABLE_PROJECTS="clang;lld" \
        -DLLVM_TARGETS_TO_BUILD="X86;RISCV" 
cmake --build . -j
cmake --build . -j -t check-all

if [ -e "llvm-build/test/tools/llvm-ar/Output/error-opening-permission.test.tmp/permission.b" ]
then
  chmod +r llvm-build/test/tools/llvm-ar/Output/error-opening-permission.test.tmp/permission.b
fi
