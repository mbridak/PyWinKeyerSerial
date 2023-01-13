#!/bin/bash
pip uninstall -y wfdlogger
rm dist/*
python3 -m build
python3 -m twine upload dist/*
