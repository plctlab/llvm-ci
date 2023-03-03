#!/bin/bash

mkdir -p llvm-build
cd llvm-build
cmake ../llvm-project/llvm -DCMAKE_BUILD_TYPE=Release -G Ninja \
        -DLLVM_ENABLE_PROJECTS="clang;lld" \
        -DLLVM_TARGETS_TO_BUILD="RISCV" 
cmake --build . -j4
ctest -j4
