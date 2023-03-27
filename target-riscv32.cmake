set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR riscv32)

set(CMAKE_C_COMPILER $ENV{LLVM_BIN_PATH}/clang)
set(CMAKE_CXX_COMPILER $ENV{LLVM_BIN_PATH}/clang++)
set(CMAKE_STRIP $ENV{LLVM_BIN_PATH}/llvm-strip)

set(triple riscv32-linux-gnu)

set(CMAKE_C_COMPILER_TARGET ${triple})
set(CMAKE_CXX_COMPILER_TARGET ${triple})
set(CMAKE_SYSROOT /usr/riscv32-linux-gnu/sysroot)
set(OPTFLAGS "${OPTFLAGS} -L/usr/riscv32-linux-gnu/lib/gcc/riscv32-unknown-linux-gnu/12.2.0 -B/usr/riscv32-linux-gnu/lib/gcc/riscv32-unknown-linux-gnu/12.2.0")
