#----------------------------------------------------------------
# Generated CMake target import file for configuration "Release".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "NCrystal::NCrystal" for configuration "Release"
set_property(TARGET NCrystal::NCrystal APPEND PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
set_target_properties(NCrystal::NCrystal PROPERTIES
  IMPORTED_LOCATION_RELEASE "${_IMPORT_PREFIX}/NCrystal/ncrystal_pyinst_data/lib/libNCrystal.so.3.9.4"
  IMPORTED_SONAME_RELEASE "libNCrystal.so.3"
  )

list(APPEND _cmake_import_check_targets NCrystal::NCrystal )
list(APPEND _cmake_import_check_files_for_NCrystal::NCrystal "${_IMPORT_PREFIX}/NCrystal/ncrystal_pyinst_data/lib/libNCrystal.so.3.9.4" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
