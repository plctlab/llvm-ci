#!/bin/bash

toolchain=$1

if [ -z UNCHANGED ] || [ ! -r result-last.json ]
then
  if [ -d llvm-test-suite-build-tmp ]
  then
    rm -rf llvm-test-suite-build-tmp
  fi
  mkdir llvm-test-suite-build-tmp
  cd llvm-test-suite-build-tmp
  reproducible_build="-Wno-builtin-macro-redefined -D__DATE__= -D__TIME__= -D__TIMESTAMP__= "
  flags="-fuse-ld=lld -static -mcpu=sifive-u74 $reproducible_build"
  export CLANG_PATH=$PWD/../llvm-build/bin
  cmake -G Ninja \
        -DCMAKE_C_FLAGS="$flags" \
        -DCMAKE_CXX_FLAGS="$flags" \
        -DOPTFLAGS="$flags" \
        -DCMAKE_TOOLCHAIN_FILE=$toolchain \
        -C ../llvm-test-suite/cmake/caches/CodeSize.cmake \
        -DTEST_SUITE_BENCHMARKING_ONLY=ON \
        -DBENCHMARK_ENABLE_TESTING=ON \
        -DTEST_SUITE_RUN_BENCHMARKS=OFF \
        ../llvm-test-suite
  cmake --build . -j
  ../llvm-build/bin/llvm-lit -j1 -o ../artifacts/result.json .
  cd ..
else
  cp result-last.json artifacts/result.json
fi

if [ -r artifacts/result.json ]
then
  if [ -r result-last.json ]
  then
    llvm-test-suite/utils/compare.py --all --metric=size --filter-hash result-last.json vs artifacts/result.json > artifacts/diff
    # small diff
    llvm-test-suite/utils/compare.py --metric=size --filter-hash result-last.json vs artifacts/result.json
  fi
  cp artifacts/result.json result-last.json
fi
