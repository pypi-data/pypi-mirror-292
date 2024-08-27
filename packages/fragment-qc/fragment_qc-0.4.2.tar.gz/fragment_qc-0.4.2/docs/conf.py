#
# Copyright 2018-2024 Fragment Contributors
# SPDX-License-Identifier: Apache-2.0
#

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

# import os
# import sys
# sys.path.insert(0, os.path.abspath("../fragment"))
# print(sys.path)


# -- Project information -----------------------------------------------------

from datetime import datetime

project = "Fragme∩t 🔨🪞"
copyright = f"2018-{datetime.now().year}Fragment Contributors"
author = "Dustin Broderick and Paige Bowling"

# The full version, including alpha/beta/rc tags
release = "0.4.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.todo",
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx_autodoc_typehints",
    "sphinx.ext.viewcode",
    "sphinxcontrib.katex",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
# html_theme = "sphinxawesome_theme"
html_static_path = ['_static']

# -- Options for Napolean output -------------------------------------------------
napoleon_google_docstring = True
napoleon_include_init_with_doc = True

# -- Options for Napolean output -------------------------------------------------
todo_include_todos = True

# -- Options for Katex output -------------------------------------------------
# katex_prerender = True # Requires NodeJS
