#!/bin/bash

############ COMMANDS NEEDED TO UPLOAD DATA TO PiPy
# TODO: Integrate this with the CI Pipeline

python3 -m build

# TESTING
# python3 -m twine upload --repository testpypi dist/*

# PRODUCTION
python3 -m twine upload --repository pypi dist/*