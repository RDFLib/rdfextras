.. rdfextras documentation master file, created by   sphinx-quickstart on Wed Sep 15 13:46:38 2010.

==================================================
RDFExtras: extension modules for use with rdflib 3
==================================================

RDFExtras is a collection of packages providing extras based on RDFLib 3. The common denominator is "non-core-rdflib".

This project is for collecting several packages with distinct uses, such as commandline tools, experimental (or unmaintained) stores and similar. It will be close to RDFLib but the intent is to keep things here a bit more loose.

These packages are thus to be considered unstable in general. Useful, sometimes near core, but not currently guaranteed to never be renamed/reshuffled/redesigned.


SPARQL
======
The SPARQL support which was removed from rdflib core is now being developed externally as various plugins. 

Pure-Python "no-SQL" SPARQL implementation
------------------------------------------
   The pure Python no-sql SPARQL implementation bits that were in the rdflib development trunk are now in :mod:`rdfextras.sparql`.

   This "default" SPARQL implementation has been developed from the original ``sparql-p`` implementation (by Ivan Herman, Dan Krech and Michel Pelletier) and over time has evolved into a full implementation of the W3C SPARQL Algebra, providing coverage for the full SPARQL grammar including all combinations of ``GRAPH``. The implementation includes unit testing and has been run against the new DAWG testsuite.

.. toctree::
   :maxdepth: 3
   
   sparql/index


Pure-Python "SPARQL-to-SQL" implementation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   The bison-parsing SPARQL2SQL implementation contributed by Chimezie Ogbuji
   et. al. has been moved to a separate branch of development 
   :mod:`rdfextras.sparql2sql` where unit tests and DAWG tests have similarly 
   been added.

.. toctree::
   :maxdepth: 3
   
   sparql2sql/index


Stores
++++++

   All of the back-end stores except for :class:`~rdflib.plugins.memory.IOMemory` 
   and  :class:`~rdflib.plugins.sleepycat.SleepyCat` have been migrated out of 
   RDFLib core and into the RDFExtras "store" module (:mod:`~rdfextras.store`)
   in order to form a separate branch of development. It is possible that some of
   these back-end stores will reappear as core RDFLib plugins.

   Extensive tests have been added in support of the development effort. 
   Contributions in this area are especially welcome.

   A new RDFLib Store plugin has been made added to the RDFExtras package - the 
   :mod:`~rdfextras.store.SPARQL` Store uses Ivan Herman et al.'s SPARQL service 
   wrapper `SPARQLWrapper <http://pypi.python.org/pypi/SPARQLWrapper>`_ to make
   a SPARQL endpoint behave programmatically like a read-only RDFLib store.

   Acknowledging a long-standing requirement, some *ad hoc* documentation has been
   rustled up to address some of the more egregious lacunae. 

.. toctree::
   :maxdepth: 3
   
   store/index


Tools
+++++

   The rdflib "tools" directory and its small collection of tools have been 
   removed from rdflib core and placed into :mod:`rdfextras.tools`.

   The collection has shrunk slightly with the removal of tools that fail to 
   build, are otherwise obsolete, and/or no longer supported by the author.

.. toctree::
   :maxdepth: 2
   
   tools/index

Utils
+++++

:mod:`rdfextras.utils` contains collections of utility functions. 

.. toctree::
   :maxdepth: 2
   
   utils/index

Web
+++++

:mod:`rdfextras.web` contains two web-apps build on the Flask microframework

.. toctree::
   :maxdepth: 2
   
   web/index


Introduction to basic tasks in rdflib 
=====================================

rdflib wiki articles transcluded here for convenience.

.. toctree::
   :maxdepth: 3

   intro_parsing
   intro_querying
   intro_mysql_as_triplestore
   intro_transitive_traversal


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
