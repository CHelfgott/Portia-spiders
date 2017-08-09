#!/bin/bash
# Script for cleaning up the prior build and regenerating for when you've
#   made code changes. May need to run with sudo.
rm -rf build
rm -rf dist
rm -rf project.egg-info
python setup.py install
