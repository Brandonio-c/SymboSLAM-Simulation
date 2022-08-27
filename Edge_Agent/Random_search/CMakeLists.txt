cmake_minimum_required(VERSION 3.21)
#compiler stuff! ---------------------------------------

set(DCMAKE_CXX_FLAGS=-stdlib=libc++)
set(DCMAKE_CXX_STANDARD 17)
set(CMAKE_C_COMPILER /usr/local/bin/gccsim)
set(CMAKE_CXX_COMPILER /usr/local/bin/g++sim)
set(CMAKE_CXX_STANDARD 17)
INCLUDE_DIRECTORIES (/usr/local/include -I /usr/X11/include)
LINK_DIRECTORIES    (/usr/local/lib /usr/X11/lib)
set (CMAKE_CXX_FLAGS "-Wall -leyesim -lX11 -std=c++17")

#compiler stuff! ---------------------------------------
project(Random_search)

IF(NOT CMAKE_BUILD_TYPE)
    SET(CMAKE_BUILD_TYPE Release)
    # SET(CMAKE_BUILD_TYPE Debug)
ENDIF()
MESSAGE("Build type: " ${CMAKE_BUILD_TYPE})



#OpenCV Stuff ---------------------------------------
SET (OpenCV_DIR /usr/local/include/opencv4)
find_package (OpenCV 4.0.0 REQUIRED)
if(NOT OpenCV_FOUND)
    message("OpenCV > 4.0.0 not found.")
    find_package(OpenCV 3.0 QUIET)
    if(NOT OpenCV_FOUND)
        message(FATAL_ERROR "OpenCV > 3.0 not found.")
    endif()
endif()
include_directories(${OpenCV_INCLUDE_DIRS})
#OpenCV Stuff ---------------------------------------


set(HEADER_FILES include/Random_Drive.h include/Wall_follow.h include/comms.h include/Local_Map.h src/read_file.cpp )
set(SOURCE_FILES src/main.cpp src/Random_Drive.cpp src/Wall_follow.cpp src/comms.cpp src/save_maps.cpp include/save_maps.h  include/read_file.h )

include_directories(
         #random search project
        ${PROJECT_SOURCE_DIR}/src
        ${PROJECT_SOURCE_DIR}/include

        ${PROJECT_SOURCE_DIR}/Third_Party/DarkHelp
        ${PROJECT_SOURCE_DIR}/Third_Party/DarkHelp/src-lib
)


link_directories(${PROJECT_SOURCE_DIR}/Third_Party/DarkHelp)
add_subdirectory(${PROJECT_SOURCE_DIR}/Third_Party/DarkHelp)

add_executable(Random_search.x  ${SOURCE_FILES} ${HEADER_FILES})

target_link_libraries(Random_search.x PUBLIC ${OpenCV_LIBS} ${PROJECT_SOURCE_DIR}/Third_Party/DarkHelp ${PROJECT_SOURCE_DIR}/Third_Party/DarkHelp/build/src-lib/libdarkhelp.a ${PROJECT_SOURCE_DIR}/Third_Party/darknet/libdarknet.so -pthread -lstdc++ -ldl)
target_compile_features(Random_search.x PRIVATE cxx_std_17)
set_property(TARGET Random_search.x PROPERTY CXX_STANDARD 17)
