# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import tomllib

# Read project info from pyproject.toml
fp = open('../../pyproject.toml', 'rb')
config = tomllib.load(fp)

info = config.get('tool', {}).get('poetry', {})

project = info.get('name', 'unknown project')
author = info.get('authors', ['unknown author'])[0].split('<')[0].strip()
copyright = f'2025, {author}'
release = info.get('version', 'unknown version')

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinx_mdinclude',
   	'sphinx.ext.coverage',
]

templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ['_static']
source_suffix = ['.rst', '.md']
coverage_show_missing_items = True

# -- Add the project directory to sys.path for module imports -----------------
sys.path.insert(0, os.path.abspath('../..'))
