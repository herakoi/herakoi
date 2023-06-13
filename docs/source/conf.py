# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'herakoi'
copyright = '2023, Michele Ginolfi, Luca Di Mascolo'
author = 'Michele Ginolfi, Luca Di Mascolo'
release = 'v0.2.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']

html_logo = 'herakoi.jpg'

# logo cyan   #53B4C8
# logo orange #E48D4C

html_theme_options = {
    "sidebar_hide_name": True,
    "dark_css_variables": {
        "color-brand-primary": "#53B4C8",
        "color-brand-content": "#53B4C8",
    },
    "light_css_variables": {
        "color-brand-primary": '#479CAD', 
        "color-brand-content": "#479CAD",
    },
}