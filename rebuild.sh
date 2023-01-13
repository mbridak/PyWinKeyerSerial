#!/bin/bash
pip uninstall -y winkeyerserial
rm dist/*
python3 -m build
pip install -e .

