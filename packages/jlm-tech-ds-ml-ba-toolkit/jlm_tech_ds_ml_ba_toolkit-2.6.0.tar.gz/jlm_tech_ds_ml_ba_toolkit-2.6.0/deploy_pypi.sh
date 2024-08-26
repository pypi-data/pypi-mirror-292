#!/bin/bash

# remove current dist folder
rm -rf dist/

# recreate the dist folder
python3 setup.py sdist

# upload to pypi
twine upload dist/*
