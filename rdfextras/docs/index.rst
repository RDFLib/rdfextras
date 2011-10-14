.. rdfextras documentation master file, created by   sphinx-quickstart on Wed Sep 15 13:46:38 2010.

==================================================
rdfextras: extension modules for use with rdflib 3
==================================================

Organisation of ``rdfextras`` extension modules
===============================================

SPARQL
------
The SPARQL support has been removed from rdflib proper and is now being developed externally as various plugins. 

Pure-Python "no-SQL"
^^^^^^^^^^^^^^^^^^^^
.. note:: The pure Python no-sql SPARQL implementation bits that were in the rdflib development trunk are now in :mod:`rdfextras.sparql`.

This "default" SPARQL implementation has been developed from the original ``sparql-p`` implementation (by Ivan Herman, Dan Krech and Michel Pelletier) and over time has evolved into a full implementation of the W3C SPARQL Algebra, providing coverage for the full SPARQL grammar including all combinations of ``GRAPH``. The implementation includes unit testing and has been run against the new DAWG testsuite.

Pure-Python "SPARQL-to-SQL"
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. note:: The bison-parsing SPARQL2SQL implementation contributed by Chimezie Ogbuji et. al. has been moved to a separate branch of development :mod:`rdfextras.sparql2sql` where unit tests and DAWG tests have similarly been added.

Stores
------
.. note:: All stores (except :class:`rdflib.plugins.memory.IOMemory` and :class:`rdflib:rdflib.plugins.sleepycat.SleepyCat`) are now in :mod:`rdfextras.store`.

Currently, one additional read-only store plugin is available:  :mod:`rdfextras.store.SPARQL`. 

Other non-core stores have been migrated to a separate branch of development, possibly to reappear as rdflib plugins. Tests have been added in support of development. Contributions in this area are especially welcome.


Tools
-----
.. note:: The rdflib "tools" directory and its small collection of tools have been removed from rdflib core and placed into :mod:`rdfextras.tools`.

The collection has shrunk slightly with the removal of tools that fail to build, are otherwise obsolete and/or no longer supported by the author.

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


Modules:
========

.. toctree::
   :maxdepth: 3
   
   sparql/index
   sparql2sql/index
   store/index
   tools/index

Epydoc API docs
===============

rdfextras epydoc `API docs <_static/api/index.html>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

