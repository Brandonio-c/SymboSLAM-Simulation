#----------------------------------------------------------------
# Generated CMake target import file for configuration "Debug".
#----------------------------------------------------------------

# Commands may need to know the format version.
set(CMAKE_IMPORT_FILE_VERSION 1)

# Import target "Darknet::dark" for configuration "Debug"
set_property(TARGET Darknet::dark APPEND PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
set_target_properties(Darknet::dark PROPERTIES
  IMPORTED_LOCATION_DEBUG "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/libdarknetd.so"
  IMPORTED_SONAME_DEBUG "libdarknetd.so"
  )

list(APPEND _IMPORT_CHECK_TARGETS Darknet::dark )
list(APPEND _IMPORT_CHECK_FILES_FOR_Darknet::dark "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/libdarknetd.so" )

# Commands beyond this point should not need to know the version.
set(CMAKE_IMPORT_FILE_VERSION)
