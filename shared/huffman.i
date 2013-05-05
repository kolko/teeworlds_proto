%module huffman
%exception { try{ $action }catch( const char *e ){ PyErr_SetString(PyExc_RuntimeError, e ); return NULL; }catch(...){ return NULL; } }
%typemap(out) bool& %{ $result=PyBool_FromLong ( *$1 ); %}
%typemap(out) char& %{ $result=PyInt_FromLong ( *$1 ); %}
%typemap(out) short& %{ $result=PyInt_FromLong ( *$1 ); %}
%typemap(out) int& %{ $result=PyInt_FromLong ( *$1 ); %}
%typemap(out) long& %{ $result=PyInt_FromLong ( *$1 ); %}
%typemap(out) float& %{ $result=PyFloat_FromDouble ( *$1 ); %}
%typemap(out) double& %{ $result=PyFloat_FromDouble ( *$1 ); %}

%typemap(in) (const void *pInput, int InputSize, void *pOutput, int OutputSize) {
   if (!PyString_Check($input)) {
       PyErr_SetString(PyExc_ValueError, "Expecting a string");
       return NULL;
   }
   $1 = (void *) PyString_AsString($input);
   $2 = PyString_Size($input);

   $4 = PyString_Size($input)*5;
   $3 = (void *) malloc($4);
}

%typemap(argout) (const void *pInput, int InputSize, void *pOutput, int OutputSize) {
   Py_XDECREF($result);   /* Blow away any previous result */
   if (result < 0) {      /* Check for I/O error */
       free($3);
       PyErr_SetFromErrno(PyExc_IOError);
       return NULL;
   }
   $result = PyString_FromStringAndSize((char *) $3, result);
   free($3);
}


%{
#include "huffman.hpp"
%}
%include "huffman.hpp"