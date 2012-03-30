.. rdfextras documentation master file, created by   sphinx-quickstart on Wed Sep 15 13:46:38 2010.

==================================================
RDFExtras: extension modules for use with rdflib 3
==================================================

RDFExtras is a collection of packages and plug-ins that provide extra functionality based on RDFLib 3. The common denominator is "non-core-rdflib".

The main RDFExtras project acts as a focal point for RDFLib-associated packages and plug-ins with distinct uses, such as SPARQL query processors (numbering one, thus far), commandline tools, serializers/parsers, experimental or unmaintained stores and similar.

.. warning:: The rdfextras packages are to be considered unstable in general. Useful, sometimes near core, but not currently guaranteed never to be renamed, refactored, reshuffled or redesigned.

Plug-ins Overview
=================

The current set of RDFLib and RDFExtras plug-ins includes RDF parsers, serializers, stores and the "sparql-p" SPARQL query processor:

.. image:: /_static/plugins-diagram.jpg
   :alt: RDFLib plug-in "archtecture"
   :align: center
   :width: 720
   :height: 475


SPARQL query processor
----------------------
The pure Python no-sql SPARQL implementation bits that were in the RDFLib development trunk are now in :mod:`rdfextras.sparql`.

This "default" SPARQL implementation has been developed from the original ``sparql-p`` implementation (by Ivan Herman, Dan Krech and Michel Pelletier) and over time has evolved into a full implementation of the W3C SPARQL Algebra, providing coverage for the full SPARQL grammar including all combinations of ``GRAPH``. The implementation includes unit testing and has been run against the new DAWG testsuite.

.. toctree::
   :maxdepth: 3
   
   sparql/index

(*The bison-parsing SPARQL2SQL implementation contributed by Chimezie Ogbuji et. al. has been moved to a separate archival branch*).

Stores
------

A new RDFLib Store plugin has been made added to the RDFExtras package - the 
:mod:`~rdfextras.store.SPARQL` Store uses Ivan Herman et al.'s SPARQL service 
wrapper `SPARQLWrapper <http://pypi.python.org/pypi/SPARQLWrapper>`_ to make
a SPARQL endpoint behave programmatically like a read-only RDFLib store.

.. warning:: The SPARQL Store API does *not* support the "initNS" keyword arg.


The other back-end stores (except for :class:`~rdflib.plugins.memory.IOMemory` 
and  :class:`~rdflib.plugins.sleepycat.SleepyCat`) have been migrated out of 
RDFLib core and into separate plug-ins.

Extensive tests have been added in support of the development effort. 
Contributions in this area are especially welcome.

Acknowledging a longstanding requirement, some *ad hoc* documentation has been
rustled up to address some of the more egregious lacunae. 

.. toctree::
   :maxdepth: 3
   
   store/index

Tools
-----

   The rdflib "tools" directory and its small collection of tools have been 
   removed from rdflib core and placed into :mod:`rdfextras.tools`.

   The collection has shrunk slightly with the removal of tools that fail to 
   build, are otherwise obsolete, and/or no longer supported by the author.

.. toctree::
   :maxdepth: 2
   
   tools/index

Utils
-----

:mod:`rdfextras.utils` contains collections of utility functions. 

.. toctree::
   :maxdepth: 2
   
   utils/index



Introduction to basic tasks in rdflib 
=====================================

rdflib wiki articles transcluded here for convenience.

.. toctree::
   :maxdepth: 3

   intro_parsing
   intro_querying
   intro_mysql_as_triplestore
   intro_transitive_traversal
   working_with

Techniques
==========


.. toctree::
   :maxdepth: 2

   extensions


Epydoc API docs
===============

rdfextras epydoc `API docs <_static/api/index.html>`_


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
