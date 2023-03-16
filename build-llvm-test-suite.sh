#!/bin/bash

repo_base=$1
run_url=$2
run_id=$3
toolchain=$repo_base/target-riscv64.cmake
update_script=$repo_base/update-binary-database.py
report_script=$repo_base/report-generate.py
metadata_script=$repo_base/embed-lnt-metadata.py

if [ $MODIFIED = 1 ] || [ ! -r result-last.json ] || [ ! -z $FORCE_REBUILD ]
then
  if [ -d llvm-test-suite-build-tmp ]
  then
    rm -rf llvm-test-suite-build-tmp
  fi
  mkdir llvm-test-suite-build-tmp
  cd llvm-test-suite-build-tmp
  # For LTO
  embed_bitcode="-Wl,--plugin-opt=-lto-embed-bitcode=optimized"
  #embed_bitcode="-fembed-bitcode "
  reproducible_build="-Qn -Wno-builtin-macro-redefined -D__DATE__= -D__TIME__= -D__TIMESTAMP__= "
  flags="-flto=thin -fuse-ld=lld -mcpu=sifive-u74 -Wno-unused-command-line-argument $embed_bitcode $reproducible_build $PATCH_ADDITIONAL_FLAGS"
  export LLVM_BIN_PATH=$PWD/../llvm-build/bin
  cmake -G Ninja \
        -DCMAKE_C_FLAGS="$flags" \
        -DCMAKE_CXX_FLAGS="$flags" \
        -DOPTFLAGS="$flags" \
        -DCMAKE_TOOLCHAIN_FILE=$toolchain \
        -C ../llvm-test-suite/cmake/caches/ReleaseThinLTO.cmake \
        -DTEST_SUITE_RUN_UNDER="$(pwd)/../../qemu.sh " \
        -DTEST_SUITE_USER_MODE_EMULATION=ON \
        -DTEST_SUITE_BENCHMARKING_ONLY=ON \
        -DBENCHMARK_ENABLE_TESTING=ON \
        -DTEST_SUITE_RUN_BENCHMARKS=ON \
        -DTEST_SUITE_COLLECT_STATS=ON \
        -DTEST_SUITE_COLLECT_COMPILE_TIME=OFF \
        ../llvm-test-suite
  cmake --build . -j
  ../llvm-build/bin/llvm-lit -j $(nproc) -o ../artifacts/result.json . >../artifacts/lit.log
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
    
    lnt runtest test_suite --import-lit artifacts/result.json --run-order=$run_id
    if [ -r report.json ]
    then
      $metadata_script report.json $(git -C ./llvm-project rev-parse HEAD) $run_url
      # submit the report to https://lnt.rvperf.org
      scp report.json plct_lnt_server:/lnt_work
      ssh plct_lnt_server "/lnt_work/submit.sh"
      mv report.json artifacts/lnt-report.json
    fi

    cp artifacts/result.json result-last.json
    git -C ./llvm-project rev-parse HEAD > llvm_revision
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
