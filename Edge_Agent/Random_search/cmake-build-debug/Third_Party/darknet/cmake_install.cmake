# Install script for directory: /home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/Third_Party/darknet

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Debug")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/libdarknetd.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/libdarknetd.so")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/libdarknetd.so"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/libdarknetd.so")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search" TYPE SHARED_LIBRARY FILES "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/cmake-build-debug/Third_Party/darknet/libdarknetd.so")
  if(EXISTS "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/libdarknetd.so" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/libdarknetd.so")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/libdarknetd.so"
         OLD_RPATH "/usr/X11/lib:/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/Third_Party/darknet:"
         NEW_RPATH "")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/libdarknetd.so")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xdevx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/darknet" TYPE FILE FILES
    "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/Third_Party/darknet/include/darknet.h"
    "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/Third_Party/darknet/include/yolo_v2_class.hpp"
    )
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/uselib" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/uselib")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/uselib"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/uselib")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search" TYPE EXECUTABLE FILES "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/cmake-build-debug/Third_Party/darknet/uselib")
  if(EXISTS "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/uselib" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/uselib")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/uselib"
         OLD_RPATH "/usr/X11/lib:/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/Third_Party/darknet:/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/cmake-build-debug/Third_Party/darknet:"
         NEW_RPATH "")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/uselib")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/darknet" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/darknet")
    file(RPATH_CHECK
         FILE "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/darknet"
         RPATH "")
  endif()
  list(APPEND CMAKE_ABSOLUTE_DESTINATION_FILES
   "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/darknet")
  if(CMAKE_WARN_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(WARNING "ABSOLUTE path INSTALL DESTINATION : ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  if(CMAKE_ERROR_ON_ABSOLUTE_INSTALL_DESTINATION)
    message(FATAL_ERROR "ABSOLUTE path INSTALL DESTINATION forbidden (by caller): ${CMAKE_ABSOLUTE_DESTINATION_FILES}")
  endif()
  file(INSTALL DESTINATION "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search" TYPE EXECUTABLE FILES "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/cmake-build-debug/Third_Party/darknet/darknet")
  if(EXISTS "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/darknet" AND
     NOT IS_SYMLINK "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/darknet")
    file(RPATH_CHANGE
         FILE "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/darknet"
         OLD_RPATH "/usr/X11/lib:/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/Third_Party/darknet:"
         NEW_RPATH "")
    if(CMAKE_INSTALL_DO_STRIP)
      execute_process(COMMAND "/usr/bin/strip" "$ENV{DESTDIR}/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/darknet")
    endif()
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  if(EXISTS "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/darknet/DarknetTargets.cmake")
    file(DIFFERENT EXPORT_FILE_CHANGED FILES
         "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/darknet/DarknetTargets.cmake"
         "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/cmake-build-debug/Third_Party/darknet/CMakeFiles/Export/share/darknet/DarknetTargets.cmake")
    if(EXPORT_FILE_CHANGED)
      file(GLOB OLD_CONFIG_FILES "$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/darknet/DarknetTargets-*.cmake")
      if(OLD_CONFIG_FILES)
        message(STATUS "Old export file \"$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/share/darknet/DarknetTargets.cmake\" will be replaced.  Removing files [${OLD_CONFIG_FILES}].")
        file(REMOVE ${OLD_CONFIG_FILES})
      endif()
    endif()
  endif()
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/darknet" TYPE FILE FILES "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/cmake-build-debug/Third_Party/darknet/CMakeFiles/Export/share/darknet/DarknetTargets.cmake")
  if("${CMAKE_INSTALL_CONFIG_NAME}" MATCHES "^([Dd][Ee][Bb][Uu][Gg])$")
    file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/darknet" TYPE FILE FILES "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/cmake-build-debug/Third_Party/darknet/CMakeFiles/Export/share/darknet/DarknetTargets-debug.cmake")
  endif()
endif()

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/darknet" TYPE FILE FILES
    "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/cmake-build-debug/Third_Party/darknet/CMakeFiles/DarknetConfig.cmake"
    "/home/brandonio/Documents/Thesis_project_2022/EyeSim_simulation_software/EyeSim/myscripts/Project_scripts/Random_search/cmake-build-debug/Third_Party/darknet/DarknetConfigVersion.cmake"
    )
endif()

