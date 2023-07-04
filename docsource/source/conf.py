# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Cow builder'
copyright = '2023, Gabe van den Hoeven'
author = 'Gabe van den Hoeven'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.intersphinx']

intersphinx_mapping = {
    'chain_simulator': ('https://bovi-analytics.github.io/chain-simulator/', None),
    'numpy': ('https://docs.scipy.org/doc/numpy/', None),
    'matplotlib': ('https://matplotlib.org/', None)
}
templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']
