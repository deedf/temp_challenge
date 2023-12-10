#!/bin/sh

pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt
(cd src; export PYTHONPATH=. ; pytest)
