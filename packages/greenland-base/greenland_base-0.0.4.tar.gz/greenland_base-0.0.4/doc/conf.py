# Configuration file for the Sphinx documentation builder.
#
# This is a generic configuration that can be plugged in as is, but
# requires jq as too to be present (and you cannot build on
# windows). If you want to avoid this requirement, you will have to
# remove the code that fills git_status, project_name and author_name
# and replace these variables in the next section by constants.

import subprocess

source_version = subprocess.run(
    ['hatch', 'version'],
    check = True, capture_output = True, encoding = 'utf-8'
).stdout.strip()

git_status = subprocess.run(
    "cd $(git rev-parse --show-toplevel); git status -s",
    check = True, capture_output = True, encoding = 'utf-8', shell = True
).stdout.strip().split("\n")

dirty = " [DIRTY]" if git_status else ""

project_name = subprocess.run(
    "hatch project metadata | jq -r .name",
    check = True, capture_output = True, encoding = 'utf-8', shell = True
).stdout.strip()

author_name = subprocess.run(
    "hatch project metadata | jq -r '.authors[0].name'",
    check = True, capture_output = True, encoding = 'utf-8', shell = True
).stdout.strip()

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project   = project_name
copyright = '2024, ' + author_name
author    = author_name
release   = source_version + dirty

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
