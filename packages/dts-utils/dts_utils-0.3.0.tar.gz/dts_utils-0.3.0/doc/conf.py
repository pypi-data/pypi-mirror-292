from importlib import metadata

# General information about the project.
project = "dts-utils"
copyright = "2024, Ledger SAS"
author = "Ledger"

# XXX:
# Project base on PEP440 and setuptools_scm dynamic versioning
# see: "Usage with Sphinx section" in https://setuptools-scm.readthedocs.io/en/stable/usage/
release: str = metadata.version(project)
version: str = ".".join(release.split(".")[:3])

root_doc = "index"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]
source_suffix = ".rst"
source_encoding = "utf-8-sig"

extensions = [
    "sphinx_rtd_theme",
    "sphinx_simplepdf",
    "sphinx.ext.todo",
    "sphinx.ext.napoleon",
    "autoapi.extension",
]

# Napoleon extension configuration
napoleon_numpy_docstring = True
napoleon_include_private_with_doc = True
napoleon_attr_annotations = True

# Autoapi configuration
autoapi_dirs = ["../src"]
autoapi_add_toctree_entry = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"


# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for HTML output ----------------------------------------------

html_theme = "sphinx_rtd_theme"

# Any idea for non outpost specific python package ?
# html_logo = '_static/figures/sentry_kernel.png'

html_static_path = ["_static"]

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#
html_use_smartypants = True

html_show_sourcelink = False

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#
html_show_sphinx = False

htmlhelp_basename = "dts-utils"

simplepdf_vars = {
    "primary": "#6299C4",
    "primary-opaque": "#6299C4",
    "secondary": "#6299C4",
    "cover": "#ffffff",
    "white": "#ffffff",
    "links": "#6299C4",
    # "cover-bg": "url(figures/outpost_fp.png) no-repeat center",
    "cover-overlay": "rgba(62, 99, 196, 0.5)",
    "top-left-content": "counter(page)",
    # "bottom-center-content": "Outpost documentation suite: Sentry kernel concepts",
}
