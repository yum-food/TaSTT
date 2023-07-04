#!/usr/bin/env bash

pushd fmt >/dev/null

mkdir build
cd build
cmake ..
cmake --build .

popd >/dev/null
