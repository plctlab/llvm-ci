set(OPTFLAGS "${OPTFLAGS} -march=rv64gczba_zbb_zbc_zbs -O3 -fomit-frame-pointer -flto=thin -DNDEBUG")

set(CMAKE_C_FLAGS_RELEASE "${OPTFLAGS}" CACHE STRING "")
set(CMAKE_CXX_FLAGS_RELEASE "${OPTFLAGS}" CACHE STRING "")
set(CMAKE_BUILD_TYPE "Release" CACHE STRING "")
