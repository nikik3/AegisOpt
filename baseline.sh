#!/bin/bash

echo "Compiling with g++ -O3..."
g++ -O3 program.cpp -o program


echo "Running baseline..."
time ./program
