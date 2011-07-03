# -*- coding: utf-8 -*-
#
# ScalyMongo documentation build configuration file, created by
# sphinx-quickstart on Sun Jul  3 12:51:42 2011.

import sys, os

# -- General configuration -----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

# General information about the project.
project = u'ScalyMongo'
copyright = u'2011, Allan Caffee'
version = '0.0'
release = '0.0.1'

exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output ---------------------------------------------------
html_theme = 'default'
html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = 'ScalyMongodoc'


# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
    'pymongo': ('http://api.mongodb.org/python/current/', None),
}
