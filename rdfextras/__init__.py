# -*- coding: utf-8 -*-
"""
The RDFExtras namespace package.
"""

__author__ = "Niklas Lindström"
__version__ = "1.0-dev"

# This is a namespace package.
try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil
    __path__ = pkgutil.extend_path(__path__, __name__)


import logging

class NullHandler(logging.Handler):
    """
    c.f.
    http://docs.python.org/howto/logging.html#library-config
    and
    http://docs.python.org/release/3.1.3/library/logging.\
    html#configuring-logging-for-a-library
    """
    def emit(self, record):
        pass

hndlr = NullHandler()
logging.getLogger("rdfextras").addHandler(hndlr)

def registerplugins():
    """
    If rdfextras is installed with setuptools, all plugins are registered
    through entry_points. This is strongly recommended. 

    If only distutils is available, the plugins must be registed manually
    This method will register all rdfextras plugins

    """

    pass # no plugins left to register
