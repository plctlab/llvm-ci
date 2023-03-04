set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR riscv64)

set(CMAKE_C_COMPILER $ENV{CLANG_PATH}/clang)
set(CMAKE_CXX_COMPILER $ENV{CLANG_PATH}/clang++)

set(triple riscv64-linux-gnu)

set(CMAKE_C_COMPILER_TARGET ${triple})
set(CMAKE_CXX_COMPILER_TARGET ${triple})
