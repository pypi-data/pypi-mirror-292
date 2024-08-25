#!/bin/bash

rm dist/*
python -m build
python -m twine upload dist/* <<< __token__

sleep 12s
pip install gm-libs -U --no-cache-dir