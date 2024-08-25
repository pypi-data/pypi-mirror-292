#ifndef DFTRACER_CONFIG_HPP
#define DFTRACER_CONFIG_HPP

/* Version string for DFTRACER */
#define DFTRACER_PACKAGE_VERSION 3.0.0
#define DFTRACER_GIT_VERSION v1.0.4

#define DFTRACER_GET_VERSION(MAJOR, MINOR, PATCH) (MAJOR * 100000 + MINOR * 100 + PATCH)
#define DFTRACER_VERSION (DFTRACER_GET_VERSION (1, 0, 4))
#define DFTRACER_VERSION_MAJOR (DFTRACER_VERSION / 100000)
#define DFTRACER_VERSION_MINOR ((DFTRACER_VERSION / 100) % 1000)
#define DFTRACER_VERSION_PATCH (DFTRACER_VERSION % 100)

/* Compiler used */
#define CMAKE_BUILD_TYPE "Release"

#define CMAKE_C_COMPILER "/usr/bin/cc"
#define CMAKE_C_FLAGS " -fPIC -Wall -Wextra -pedantic -Wno-unused-parameter -Wno-deprecated-declarations"
#define CMAKE_C_FLAGS_DEBUG "-g"
#define CMAKE_C_FLAGS_RELWITHDEBINFO "-O2 -g -DNDEBUG"
#define CMAKE_C_FLAGS_RELEASE " -fPIC -Wall -Wextra -pedantic -Wno-unused-parameter -Wno-deprecated-declarations_RELEASE"

#define CMAKE_CXX_COMPILER "/usr/bin/c++"
#define CMAKE_CXX_FLAGS " -fPIC -Wall -Wextra -pedantic -Wno-unused-parameter -Wnon-virtual-dtor -Wno-deprecated-declarations"
#define CMAKE_CXX_FLAGS_DEBUG "-g"
#define CMAKE_CXX_FLAGS_RELWITHDEBINFO "-O2 -g -DNDEBUG"
#define CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG"

/* #undef CMAKE_C_SHARED_LIBRARY_FLAGS */
/* #undef CMAKE_CXX_SHARED_LIBRARY_FLAGS */

/* Macro flags */
/* #undef DFTRACER_GNU_LINUX */

//==========================
// Common macro definitions
//==========================

#define DFTRACER_PATH_DELIM "/"

// #define DFTRACER_NOOP_MACRO do {} while (0)
#define DFTRACER_NOOP_MACRO

// Detect VAR_OPT
// https://stackoverflow.com/questions/48045470/portably-detect-va-opt-support
#if __cplusplus <= 201703 && defined __GNUC__ && !defined __clang__ && \
    !defined __EDG__
#define VA_OPT_SUPPORTED false
#else
#define PP_THIRD_ARG(a, b, c, ...) c
#define VA_OPT_SUPPORTED_I(...) PP_THIRD_ARG(__VA_OPT__(, ), true, false, )
#define VA_OPT_SUPPORTED VA_OPT_SUPPORTED_I(?)
#endif

#if !defined(DFTRACER_HASH_SEED) || (DFTRACER_HASH_SEED <= 0)
#define DFTRACER_SEED 104723u
#endif

#endif /* DFTRACER_CONFIG_H */
