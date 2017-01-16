cmake_minimum_required(VERSION 3.5)
project(reliapy)
add_subdirectory(relia)
set(CMAKE_CXX_STANDARD 14)

include_directories(/usr/include/python3.5m
        relia)
add_definitions(-DLOG_LEVEL_1)
add_definitions(-DUSE_STDOUT)
set(SOURCE_FILES
        API_wrap.cxx
        API.cpp
        API.h)

add_library(reliapy SHARED ${SOURCE_FILES})
target_link_libraries(reliapy relia)