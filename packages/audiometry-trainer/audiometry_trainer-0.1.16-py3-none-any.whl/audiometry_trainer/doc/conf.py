# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'audiometry_trainer'
copyright = '2023-2024, Samuele Carcagno'
author = 'Samuele Carcagno'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = "0.1.16"
# The full version, including alpha/beta/rc tags.
release = "0.1.16"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# localization
locale_dirs = ['locale/']   # path is example but recommended.
gettext_compact = False     # optional.
#language = "fr"
#latex_engine = 'lualatex'
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '12pt',
    'fncychap': r'\usepackage[Bjornstrup]{fncychap}',
    #'fncychap': ''
    'extraclassoptions': 'openany,oneside',
    #'fontpkg': '\\usepackage{libertinus}'
    #'fontpkg': '\\usepackage{mathpazo,bm}
    'sphinxsetup': 'verbatimwithframe=true'
    }

numfig = True
#figure_language_filename = "{path}/{language}/{basename}{ext}"
