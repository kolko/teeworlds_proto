#PY=/usr/include/python2.7
#huffman : huffman.py huffman.o;
#huffman.py huffman_wrap.cxx : huffman.i huffman.hpp
#	swig -c++ -python huffman.i
#huffman_wrap.o : huffman_wrap.cxx huffman.hpp
#	g++ -I$(PY) -c huffman_wrap.cxx
#huffman.o : huffman.hpp huffman.cpp
#	g++ -I$(PY) -Ibase -I/ -c huffman.cpp
#_huffman.so : huffman_wrap.o huffman.o
#	g++ -shared -o _huffman.so huffman_wrap.o huffman.o


name = huffman
headers = huffman.hpp #system.h
modules = huffman.cpp #system.c
include ab
