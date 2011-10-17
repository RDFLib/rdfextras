# -*- coding: utf-8 -*-
#
#
# $Date: 2005/11/04 14:06:36 $, by $Author: ivan $, $Revision: 1.1 $
# The documentation of the module, hence the convention for the documentation
# of methods and classes, is based on the epydoc tool.  This tool parses
# Python source files and generates API descriptions XHTML.
# The latest release of epydoc (version 2.0) can be downloaded from
# <a href="http://pypi.python.org/pypi/epydoc/3.0.1">PyPi</a>.
#

"""
Historical note
---------------

    **SPARQL implementation on top of RDFLib**
    
    Implementation of the `W3C SPARQL <http://www.w3.org/TR/rdf-sparql-query/>`_ 
    language (version April 2005). The basic class here is supposed to be a 
    superclass of :class:`~rdfextras.sparql.graph.SPARQLGraph`; it has been separated only for 
    a better maintainability.

    For a general description of the SPARQL API, see the separate, more complete
    `description <http://dev.w3.org/cvsweb/%7Echeckout%7E/2004/PythonLib-IH/Doc/sparqlDesc.html>`_.

    **History**

    * Version 1.0: based on an earlier version of the SPARQL, first released implementation

    * Version 2.0: version based on the March 2005 SPARQL document, also a major change of the core code (introduction of the separate ``GraphPattern`` :class:`rdflibUtils.graph.GraphPattern` class, etc).

    * Version 2.01: minor changes only: - switch to epydoc as a documentation tool, it gives a much better overview of the classes - addition of the SELECT * feature to sparql-p

    * Version 2.02: - added some methods to ``myTripleStore`` :class:`rdflibUtils.myTripleStore.myTripleStore` to handle ``Alt`` and ``Bag`` the same way as ``Seq`` - added also methods to :meth:`add` collections and containers to the triple store, not only retrieve them

    * Version 2.1: adapted to the inclusion of the code into rdflib, thanks to Michel Pelletier

    * Version 2.2: added the sorting possibilities; introduced the Unbound class and have a better interface to patterns using this (in the BasicGraphPattern class)


    :author: `Ivan Herman <http://www.ivan-herman.net>`_

    :license: This software is available for use under the

    `W3C Software License <http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231>`_

    :contact: Ivan Herman, ivan@ivan-herman.net

    :version: 2.2

"""

from rdflib import URIRef

DESCRIBE = URIRef('http://www.w3.org/TR/rdf-sparql-query/#describe')

__version__ = "2.2"

Debug = False

# Note that the SPARQL draft allows the usage of a different query character,
# but I decided not to be that generous, and keep to one only. I put it into
# a separate variable to avoid problems if the group decides to change the
# syntax on that detail...
_questChar  = "?"

############################################################################################

class Processor(object):
    ""
    def __init__(self, graph):
        pass
    
    def query(self, strOrQuery, initBindings={}, initNs={}, DEBUG=False):
        ""
        pass
    

from rdflib.exceptions  import Error

##
# SPARQL Error Exception (subclass of the RDFLib Exceptions)
class SPARQLError(Error):
    """A SPARQL error has been detected"""
    def __init__(self,msg):
        Error.__init__(self, ("SPARQL Error: %s." % msg))
    


