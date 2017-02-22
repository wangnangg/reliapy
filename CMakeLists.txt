cmake_minimum_required(VERSION 3.5)
project(reliapy)
add_subdirectory(relia)
set(CMAKE_CXX_STANDARD 14)

include_directories(/usr/include/python3.6m
        relia)
add_definitions(-DELPP_FEATURE_PERFORMANCE_TRACKING)
set(SOURCE_FILES
        API_wrap.cxx
        API.cpp
        API.h)

add_library(reliapy SHARED ${SOURCE_FILES})
target_link_libraries(reliapy relia)