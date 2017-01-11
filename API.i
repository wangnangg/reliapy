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

%typemap(throws) Exception %{
  PyErr_SetString(PyExc_RuntimeError, $1.what());
  SWIG_fail;
%}

%include "relia/ExportType.h"
%include "std_vector.i"
namespace std {
  %template(NodeVec) vector<Node>;
  %template(EdgeVec) vector<Edge>;
}

%include "API.h"
