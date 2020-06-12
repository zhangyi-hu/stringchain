#!/usr/bin/env bash

declare -a versions=("3.7" "3.8")

rm -rf dist/*

for version in ${versions[*]}; do
  conda build . --output-folder dist --py "$version"
done

# this script works on mac, change osx-64 to your platform if you want to use it:
# linux-32 linux-64 linux-aarch64 linux-armv6l linux-armv7l linux-ppc64le osx-64 win-32 win-64
conda convert --platform all dist/osx-64/stringchain* -o dist

# run this line if you want to upload the built packages to anaconda cloud
# anaconda upload dist/*/stringchain*.tar.bz2
