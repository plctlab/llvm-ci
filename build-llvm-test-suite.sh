#!/bin/bash

repo_base=$1
run_url=$2
toolchain=$repo_base/target-riscv64.cmake
update_script=$repo_base/update-binary-database.py
report_script=$repo_base/report-generate.py

if [ $MODIFIED = 1 ] || [ ! -r result-last.json ] || [ ! -z $FORCE_REBUILD ]
then
  if [ -d llvm-test-suite-build-tmp ]
  then
    rm -rf llvm-test-suite-build-tmp
  fi
  mkdir llvm-test-suite-build-tmp
  cd llvm-test-suite-build-tmp
  # For LTO: -mllvm -lto-embed-bitcode=optimized
  embed_bitcode="-fembed-bitcode "
  reproducible_build="-Qn -Wno-builtin-macro-redefined -D__DATE__= -D__TIME__= -D__TIMESTAMP__= "
  flags="-fuse-ld=lld -mcpu=sifive-u74 -Wno-unused-command-line-argument $embed_bitcode $reproducible_build $PATCH_ADDITIONAL_FLAGS"
  export CLANG_PATH=$PWD/../llvm-build/bin
  cmake -G Ninja \
        -DCMAKE_C_FLAGS="$flags" \
        -DCMAKE_CXX_FLAGS="$flags" \
        -DOPTFLAGS="$flags" \
        -DCMAKE_TOOLCHAIN_FILE=$toolchain \
        -C ../llvm-test-suite/cmake/caches/ReleaseThinLTO.cmake \
        -DTEST_SUITE_BENCHMARKING_ONLY=ON \
        -DBENCHMARK_ENABLE_TESTING=ON \
        -DTEST_SUITE_RUN_BENCHMARKS=OFF \
        -DTEST_SUITE_COLLECT_COMPILE_TIME=OFF \
        ../llvm-test-suite
  cmake --build . -j
  ../llvm-build/bin/llvm-lit -j1 -o ../artifacts/result.json . > /dev/null
  if [ -z $PRE_COMMIT_MODE ]
  then
    $update_script . ../binaries
  fi
  cd ..
else
  echo "Skip llvm-test-suite tests"
  cp result-last.json artifacts/result.json
fi

if [ -r artifacts/result.json ]
then
  if [ -r result-last.json ]
  then
    llvm-test-suite/utils/compare.py --all --metric=size --filter-hash result-last.json vs artifacts/result.json > artifacts/diff
    # small diff
    llvm-test-suite/utils/compare.py --metric=size --filter-hash result-last.json vs artifacts/result.json
    $report_script result-last.json artifacts/result.json . $run_url
    echo "SHOULD_OPEN_ISSUE=$?" >> $GITHUB_OUTPUT
    if [ -d artifacts/binaries ]
    then
      tar -czf artifacts/binaries.tar.gz artifacts/binaries
      rm -rf artifacts/binaries
    fi
  fi
  if [ -z $PRE_COMMIT_MODE ]
  then
    cp artifacts/result.json result-last.json
  fi
fi

if [ -r artifacts/issue_generated.md ]
then
  cp artifacts/issue_generated.md $repo_base/issue.md
fi

if [ -r artifacts/pr-comment_generated.md ]
then
  cp artifacts/pr-comment_generated.md $repo_base/pr-comment.md
fi

exit 0
