#!/bin/bash

toolchain=$1

mkdir -p llvm-test-suite-build-tmp
cd llvm-test-suite-build-tmp
flags="-fuse-ld=lld -static -mcpu=sifive-u74"
cmake -DCMAKE_C_COMPILER=../llvm-build/bin/clang -DCMAKE_C_COMPILER=../llvm-build/bin/clang++ -G Ninja \
      -DCMAKE_C_FLAGS=$flags \
      -DCMAKE_CXX_FLAGS=$flags \
      -DOPTFLAGS=$flags \
      -DCMAKE_TOOLCHAIN_FILE=$toolchain \
      -C ../llvm-test-suite/cmake/caches/CodeSize.cmake \
      -DTEST_SUITE_BENCHMARKING_ONLY=ON \
      -DBENCHMARK_ENABLE_TESTING=OFF \
      ../llvm-test-suite
cmake --build . -j
