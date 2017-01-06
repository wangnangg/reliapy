%module reliapy
%{
#include "API.h"
%}
%typemap(in) PyObject {
    if (!PyCallable_Check($input)) {
        PyErr_SetString(PyExc_TypeError, "Need a callable object!");
        return NULL;
    }
    $1 = $input;
 }

%typemap(in) PyObject {
    if (!PyCapsule_CheckExact($input)) {
        PyErr_SetString(PyExc_TypeError, "Need a PyCapsule object!");
        return NULL;
    }
    $1 = $input;
 }

%typemap(in) PyObject {
    if ($input != Py_None) {
        PyErr_SetString(PyExc_TypeError, "Need a None object!");
        return NULL;
    }
    $1 = $input;
 }
%include "API.h"
