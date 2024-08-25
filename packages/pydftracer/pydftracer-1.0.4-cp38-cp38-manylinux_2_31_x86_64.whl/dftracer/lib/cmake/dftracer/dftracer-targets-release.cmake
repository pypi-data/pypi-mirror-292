#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "dftracer" for configuration "Release"
set_property(TARGET dftracer APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dftracer PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libdftracer.so.3.0.0"
  IMPORTED_SONAME_RELEASE "libdftracer.so.3.0.0"
  )

list(APPEND _cmake_import_check_targets dftracer )
list(APPEND _cmake_import_check_files_for_dftracer "${_IMPORT_PREFIX}/lib/libdftracer.so.3.0.0" )

# Import target "dftracer_preload" for configuration "Release"
set_property(TARGET dftracer_preload APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(dftracer_preload PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/lib/libdftracer_preload.so"
  IMPORTED_SONAME_RELEASE "libdftracer_preload.so"
  )

list(APPEND _cmake_import_check_targets dftracer_preload )
list(APPEND _cmake_import_check_files_for_dftracer_preload "${_IMPORT_PREFIX}/lib/libdftracer_preload.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
