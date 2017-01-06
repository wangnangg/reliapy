.PHONY: all
all: _reliapy.so reliapy.py
cmake-build-debug/libreliapy.so: cmake-build-debug/Makefile API_wrap.cxx
	make -C cmake-build-debug
cmake-build-debug/Makefile: CMakeLists.txt
	cmake ./cmake-build-debug
_reliapy.so: cmake-build-debug/libreliapy.so
	cp cmake-build-debug/libreliapy.so _reliapy.so
reliapy.py: API.i API.h
	swig -python -c++ API.i
API_wrap.cxx: API.i API.h
	swig -python -c++ API.i

init: API_wrap.cxx
	mkdir -p cmake-build-debug
	cd cmake-build-debug && cmake -DCMAKE_BUILD_TYPE=Debug -G "CodeBlocks - Unix Makefiles" ../
