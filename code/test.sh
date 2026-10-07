#!/bin/sh
# Offline tests for the product. No network, no keys. Run from anywhere:  code/test.sh
# tests/nonet.py removes the live keys and turns the Jev gate off for every test.
set -e
cd "$(dirname "$0")"
exec python3 -m unittest discover -s tests "$@"
