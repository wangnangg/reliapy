config:=debug
.PHONY: all
all: _reliapy.so reliapy.py
cmake-build-${config}/libreliapy.so: API_wrap.cxx FORCE
	cmake --build cmake-build-${config} --target reliapy -- -j 4
_reliapy.so: cmake-build-${config}/libreliapy.so
	cp cmake-build-${config}/libreliapy.so _reliapy.so
reliapy.py: API.i API.h
	swig -python -c++ API.i
API_wrap.cxx: API.i API.h
	swig -python -c++ API.i

init: API_wrap.cxx
	mkdir -p cmake-build-${config}
	cd cmake-build-${config} && cmake -DCMAKE_BUILD_TYPE=${config} -G "CodeBlocks - Unix Makefiles" ../

FORCE: ;
