#!/bin/sh
# Rebuild site/, the finished JupyterLite site Tofu serves, from this repository.
# Needs a Python 3.11 environment with this repository's requirements installed and active:
#   python3.11 -m venv ../jupyterlite-venv && . ../jupyterlite-venv/bin/activate
#   python -m pip install -r requirements.txt
# Then commit with `git add -f site` (upstream's .gitignore ignores a top-level site/ folder).
set -eu
cd "$(dirname "$0")/.."
rm -rf site
# The same build upstream's GitHub Pages workflow runs (it copies README.md into content/ first).
jupyter lite build --contents content --contents README.md --output-dir site
python -I tofu/adapt_site.py site
