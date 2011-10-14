# -*- coding: UTF-8 -*-
"""
The RDFExtras namespace package.
"""

__author__ = "Niklas Lindström"
__version__ = "0.2-dev"

# This is a namespace package.
try:
    import pkg_resources
    pkg_resources.declare_namespace(__name__)
except ImportError:
    import pkgutil
    __path__ = pkgutil.extend_path(__path__, __name__)

from rdfextras import sparql

# c.f.
# http://docs.python.org/howto/logging.html#library-config
# and
# http://docs.python.org/release/3.1.3/library/logging.html#configuring-logging-for-a-library

import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

h = NullHandler()
logging.getLogger("rdfextras").addHandler(h)

